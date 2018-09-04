module AwjTeacherConcern
  module StarRate
    extend ActiveSupport::Concern

    included do
      has_many :star_snapshots, class_name: 'AwjTeacherStarSnapshot', dependent: :destroy
      after_commit :initialize_star_rate, on: :create
    end

    # 最新的有效的星级数据快照
    def active_star_snapshot
      star_snapshots.active.last
    end

    # new teacher star rate (v2)
    def current_star_rate
      @current_star_rate ||= active_star_snapshot&.star_rate || 1
    end

    # 取最近5次QC平均分，不满5次的话，取中位数（暂定3.75, 注意一定要落在last_five_qc_score_rate 0.025这个档位里）
    def last_five_qc_score_cache(force_refresh=false)
      ::Utils::CacheUtil::CacheTool.improve_by_cache("teacher_#{self.id}_last_five_qc_score", {expired_after: 1.day, force_refresh: force_refresh}) do
        qcs = self.awjcls_lesson_qcs.where.not(score: nil).order('updated_at desc').limit(5)
        qcs.size == 5 ? (qcs.map(&:score).inject(&:+).to_f / 5) : 3.75
      end
    end

    def last_five_qc_score_rate(force_refresh=false)
      last_five_qc_score_cache(force_refresh) * 0.005
    end

    private

    def initialize_star_rate
      AwjTeacherStarSnapshot.initialize_star_rate_for_teacher!(self)
    end
  end
end
