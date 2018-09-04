select
 qc.id as qc_id,
  qc.awj_teacher_id,
  concat_ws(' ',t.first_name,t.last_name)as teacher_name,
  qc.awjcls_lesson_id,
  cl.start_time,
  cl.end_time,
  ac.name as course_name,
  act.type_name as class_type_name,
  s2.name as hq_name,
  qc.assigned_at,
  qc.score_recorded_at,
  qc.score,
  qc.notes,
  case qc.result when 0 then 'pass'
    when 1 then 'not_pass'
    when 2 then 'cannot_qc'
    end as result,
  case qc.qc_advice when 1 then 'normal'
    when 3 then 'qc_again'
    when 5 then 'train_teacher'
    when 7 then 'adjust'
    when 9 then 'deactive_teacher'
      end as qc_adive,
  case qc.trigger_event when 0 then 'operation_arrange'
    when 1 then 'new_teacher'
    when 2 then 'new_course'
    when 3 then 'random'
    when 4 then 'student_bad_feedback'
    when 5 then 'new_school'
    when 6 then 'course'
    when 7 then 'abnormal_track'
    end as trigger_event,
  qcl.whodunnit as qcer
  from awjcls_lesson_qcs qc
  join awjcls_lesson_qc_logs qcl on qc.id = qcl.awjcls_lesson_qc_id and qc.score = qcl.score
  join awj_teachers t on qc.awj_teacher_id = t.id and t.is_virtual= 0 and t.organization = 'PDD'
  join awjcls_lessons cl on qc.awjcls_lesson_id = cl.id and cl.state <> 6
  join awjcls_classes c on cl.awjcls_class_id = c.id  and c.state =2
  left join awj_courses ac on c.awj_course_id = ac.id
  left join awjcls_class_types act on c.awjcls_class_type_id = act.id
  join awj_schools s1 on c.awj_school_id = s1.id
  left join awj_schools s2 on s1.hq_code = s2.code and s2.formal_hq_school = 1
  where qc.score is not null and qcl.score is not null
  and qcl.whodunnit is not null