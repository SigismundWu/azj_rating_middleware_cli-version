class AwjTeacherStarSnapshot < BaseModel
  belongs_to :awj_teacher
  belongs_to :operator, class_name: 'AwjUser'

  enum state: [:inactive, :active]
  enum created_source: [:from_system_settle, :from_setting_update, :from_operator_change, :from_new_teacher]

  validates_presence_of :awj_teacher_id, :behavior_month, :star_rate, :state, :created_source
  validates_uniqueness_of :awj_teacher_id, scope: :state, if: Proc.new {|snapshot| snapshot.active? }

  scope :have_behavior, -> { where.not(behavior_score: nil) }
  scope :no_hehavior, -> { where(behavior_score: nil) }
  scope :except_manual_change, -> { where.not(created_source: AwjTeacherStarSnapshot.created_sources['from_operator_change']) }

  class << self
    # 每个星级对应的最低分数
    [:five_star_rate, :four_star_rate, :three_star_rate, :two_star_rate, :one_star_rate].each do |x|
      define_method("#{x}_min_score") do
        return 0 if sorted_total_score.size == 0
        rate = AwjTeacherAssignmentSetting.instance.send(x)
        rate_index = (sorted_total_score.size * rate).round
        sorted_total_score[rate_index-1]
      end
    end

    def existing_data_last_month_str
      AwjTeacherStarSnapshot.active.order('id asc').last&.behavior_month
    end

    # 找到最后一条数据所统计的月份, 如果是已经有上个月冻结的数据，则不再查
    def need_to_settle_snapshots?
      if existing_data_last_month_str
        year = existing_data_last_month_str.first(4).to_i
        month = existing_data_last_month_str.last(2).to_i
        last_existing_month = Date.new(year, month)
        return false if last_existing_month == Date.today.beginning_of_month - 1.month
      end
      return true
    end

    # 请求到最新一个周期的老师behavior数据，存入数据库
    def settle_snapshots!(month_str=nil)
      return "本周期老师行为分数已存入数据库，无需重复获取" unless need_to_settle_snapshots?

      request_month_str = month_str || (Date.today.beginning_of_month - 1.month).strftime("%Y%m")
      teacher_behavior_api = "#{IYY_SERVER}/intra_api/v1/awj_teacher_monthly_grades"
      payload = {
        settle_month_filter: request_month_str
      }
      params = generate_access_params_to_iyy_api(payload)
      # for test
      # params = {api_key: '15601681225'}.merge(payload)
      begin
        resp = RestClient.get teacher_behavior_api, {params: params}
        h = JSON.parse resp.body
        if h['data'].present?
          ActiveRecord::Base.transaction do
            all_teacher_ids = AwjTeacher.real.pluck(:id)
            settle_teacher_ids = h['data'].map{|x| x['attributes']['awj-teacher-id'] }
            # 先将目前active的数据inactive
            self.active.update_all(state: self.states['inactive'], updated_at: Time.now)
            # 给每个API拉到的老师算出最新的performance总分, 创建新的快照
            self.bulk_insert do |worker|
              h['data'].each do |data|
                awj_teacher_id = data['attributes']['awj-teacher-id']
                teacher = AwjTeacher.find(awj_teacher_id)
                qc_score = teacher.last_five_qc_score_rate(true)
                worker.add({
                  awj_teacher_id: awj_teacher_id,
                  state: AwjTeacherStarSnapshot.states['active'],
                  behavior_month: data['attributes']['settle-month'],
                  behavior_score: data['attributes']['grade'].to_f,
                  qc_score: qc_score,
                  total_score: qc_score + data['attributes']['grade'].to_f,
                  created_source: AwjTeacherStarSnapshot.created_sources['from_system_settle']
                })
              end
            end
            # 给其他没有behavior_score的老师，赋一个中间的总分和星级
            self.bulk_insert do |worker|
              (all_teacher_ids - settle_teacher_ids).each do |teacher_id|
                worker.add({
                  awj_teacher_id: teacher_id,
                  behavior_month: request_month_str,
                  state: AwjTeacherStarSnapshot.states['active'],
                  created_source: AwjTeacherStarSnapshot.created_sources['from_system_settle']
                })
              end
            end
            # 再计算相应的星级，注意来源为"from_system_settle"
            set_star_rate_for_active_teachers!(source: 'from_system_settle')
            set_star_rate_for_inactive_teachers!(source: 'from_system_settle')
          end
          message = "成功从iyy拉取到老师#{request_month_str}的行为数据！"
        elsif h['error'].present?
          message = h['error']
        end
      rescue RestClient::BadRequest => e
        message = '计算星级失败，请求iyy出现错误, 老师上个月行为数据还未冻结'
      end
      logger.info message
      return message
    end

    # 重新生成新一代的active星级数据，发生于运营调整了星级比例
    def refresh_snapshots!
      # 先将目前active的数据inactive，注意不要inactive人工调整过星级的数据
      old_snapshots = self.active.except_manual_change.to_a
      ActiveRecord::Base.transaction do
        self.active.except_manual_change.update_all(state: self.states['inactive'], updated_at: Time.now)
        # 再copy生成新一代的active数据
        self.bulk_insert do |worker|
          old_snapshots.each do |snapshot|
            worker.add(snapshot.attributes.slice('awj_teacher_id', 'behavior_month', 'behavior_score', 'qc_score', 'total_score').merge({
              state: AwjTeacherStarSnapshot.states['active'],
              created_source: AwjTeacherStarSnapshot.created_sources['from_setting_update']
            }))
          end
        end
        # 再计算相应的星级，注意来源为"from_setting_update"
        set_star_rate_for_active_teachers!(source: 'from_setting_update')
        set_star_rate_for_inactive_teachers!(source: 'from_setting_update')
      end
    end

    def initialize_star_rate_for_teacher!(teacher)
      return if AwjTeacherStarSnapshot.active.empty?
      return if teacher.active_star_snapshot.present?
      ActiveRecord::Base.transaction do
        self.create!({
          awj_teacher_id: teacher.id,
          behavior_month: self.existing_data_last_month_str,
          state: 'active',
          star_rate: 3,
          created_source: 'from_new_teacher'
        })
      end
    end

    # 总分中位数
    def median_total_score
      len = sorted_total_score.size
      return 0 if len == 0
      (sorted_total_score[(len - 1) / 2] + sorted_total_score[len / 2]) / 2.0
    end

    def median_score_star_rate
      corresponding_star_rate(median_total_score)
    end

    # 根据分数算出对应的星级
    def corresponding_star_rate(score)
      return 0 if sorted_total_score.size == 0
      case score
      when five_star_rate_min_score..sorted_total_score.first
        5
      when four_star_rate_min_score...five_star_rate_min_score
        4
      when three_star_rate_min_score...four_star_rate_min_score
        3
      when two_star_rate_min_score...three_star_rate_min_score
        2
      when one_star_rate_min_score...two_star_rate_min_score
        1
      else
        0
      end
    end

    private

    # 从高到低排序
    def sorted_total_score
      active.have_behavior.map(&:total_score).sort.reverse
    end

    # 对于所有最新的有behavior_score的snapshot, 根据awj_teacher_assignment_setting里的星级比例设置，算出星级
    # 但是注意不要改变人工调整过的数据
    def set_star_rate_for_active_teachers!(source:)
      s = created_sources[source]
      active.have_behavior.except_manual_change.each do |snapshot|
        snapshot.star_rate = corresponding_star_rate(snapshot.total_score)
        snapshot.created_source = s
        snapshot.save!
      end
    end

    # 对于所有最新的没有behavior_score的snapshot, 取有behavior_score的snapshots的中位星级，赋值
    # 现在临时改为直接设置为3星
    def set_star_rate_for_inactive_teachers!(source:)
      s = created_sources[source]
      active.no_hehavior.except_manual_change.update_all(star_rate: 3, created_source: s, updated_at: Time.now)
    end

    def generate_access_params_to_iyy_api(business_params)
      params_hash = business_params.merge({
        :app_id => IYY_APP_ID,
        :timestamp => (Time.now.to_f * 1000).to_i
      })
      string_to_sign = params_hash.to_param + "&secret=#{IYY_APP_SECRET}"
      sign = Digest::SHA256.hexdigest(string_to_sign)
      return params_hash.merge({ :sign => sign })
    end
  end
end
