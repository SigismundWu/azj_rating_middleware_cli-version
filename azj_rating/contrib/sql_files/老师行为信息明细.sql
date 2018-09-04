
(select
  iams.awj_teacher_id,
  ias.awj_lesson_id,
  ias.teacher_status_for_lesson,
  ias.ask_for_leave_advanced_minutes,
  act.ename as 上课类型,
  ias.category_desc as 教材,
  ias.lesson_headschool_name as 机构,
  c.id as 班级id,
  cl.start_time,
  cl.end_time,
  ac.check_zoom_first_live_at as actual_start_time,
  ac.check_zoom_last_live_at as actual_end_time,
  case when ias.teacher_status_for_lesson in ('normal_lesson','abnormal_lesson') and ias.freezed_salary_base > 0  then
    case when cl2.mintm is not null then 25+abs(timestampdiff(SECOND,cl.end_time, cl.start_time))/3600*2 else
     abs(timestampdiff(SECOND,cl.end_time, cl.start_time))/3600*2 end
      when ias.teacher_status_for_lesson = 'late' and late_minutes <= 5 and cl2.mintm is not null then 20
      when ias.teacher_status_for_lesson = 'late' and late_minutes <= 5 and  cl2.mintm is null then -5
      when (ias.teacher_status_for_lesson like '%no_show%'or (ias.teacher_status_for_lesson = 'ask_for_leave' and ias.ask_for_leave_advanced_minutes <=30)) and ias.is_deduction_exempted <> 1 then -1000
      when ias.teacher_status_for_lesson = 'ask_for_leave' and ias.ask_for_leave_advanced_minutes <= 2880 then -10
      when ias.teacher_status_for_lesson = 'ask_for_leave' and ias.ask_for_leave_advanced_minutes <= 43200 then -5
      else 0
      end as 积分变化
  from iyy_awj_salary_settle_items ias
  join iyy_awj_salary_month_settlements iams on ias.iyy_awj_salary_month_settlement_id = iams.id
  join awjcls_lessons cl on ias.awj_lesson_id =cl.id and cl.state <> 6
  join awjcls_classes c on cl.awjcls_class_id = c.id and c.state = 2
  join awj_teachers t on iams.awj_teacher_id = t.id and t.is_virtual = 0 and t.organization = 'PDD'
  left join (select iams.awj_teacher_id,min(ias.lesson_start_time)as mintm
     from iyy_awj_salary_settle_items ias
       join iyy_awj_salary_month_settlements iams on ias.iyy_awj_salary_month_settlement_id = iams.id
       join awjcls_lessons cl on ias.awj_lesson_id = cl.id  and cl.state <>6
       join awjcls_classes c on cl.awjcls_class_id =c.id and c.state = 2
     where ias.freezed =1 and ias.teacher_status_for_lesson in ('normal_lesson','abnormal_lesson','late') and ias.freezed_salary_base > 0
       and (ias.late_minutes is null or ias.late_minutes <= 5)
     group by 1)cl2 on iams.awj_teacher_id = cl2.awj_teacher_id and ias.lesson_start_time = cl2.mintm
  left join awjcls_class_types act on ias.awjcls_class_type_id = act.id
  left join awjcls_classrooms ac on ias.awj_lesson_id = ac.awjcls_lesson_id
where ias.awj_lesson_id is not null and ias.freezed = 1 and ias.is_deleted <> 1)
union
(select
   ta.awj_teacher_id,
   cl.id,
  'ask_for_leave' as status,
  TIMESTAMPdiff(minute,ta.created_at,cl.start_time)as adminutes,
  act.ename,
  acc.name as 教材,
  sch2.name as 机构,
  c.id as 班级id,
  cl.start_time,
  cl.end_time,
  ac2.check_zoom_first_live_at,
  ac2.check_zoom_last_live_at,
  case when TIMESTAMPdiff(minute,ta.created_at,cl.start_time) <= 30 then -1000
    when TIMESTAMPdiff(minute,ta.created_at,cl.start_time) <=2880 then -10
    when TIMESTAMPdiff(minute,ta.created_at,cl.start_time) <= 43200 then -5
    else 0 end
  from awj_teacher_absences ta
  join awj_conflict_requests cr on ta.id = substr(cr.trigger_event_object, 15 , length(cr.trigger_event_object )-15) and cr.state = 3
  join awj_conflict_lessons cfl on cr.id = cfl.awj_conflict_request_id
  join awjcls_lessons cl on cfl.lesson_id = cl.id and cl.state <> 6
  join awjcls_classes c on cl.awjcls_class_id = c.id
  join awj_courses ac on c.awj_course_id = ac.id
  join awj_course_categories acc on ac.awj_course_category_id = acc.id
  join awj_schools sch on c.awj_school_id = sch.id
  left join awj_schools sch2 on sch.hq_code = sch2.code
  join awjcls_class_types act on c.awjcls_class_type_id = act.id
    join awj_teachers t on ta.awj_teacher_id = t.id and t.is_virtual = 0 and t.organization = 'PDD'
  left join awjcls_classrooms ac2 on cl.id = ac2.awjcls_lesson_id
where ta.canceled_at is null and date(cl.start_time)< '2017-10-01');
