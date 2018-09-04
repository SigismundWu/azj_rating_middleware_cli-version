select af.id as 评价id,
  af.created_at as 评价时间,
  alr.awjcls_lesson_id,
  cl.awj_teacher_id,
  cl.start_time as 课程开始时间,
  cl.end_time as 课程结束时间,
  case af.score when 0 then '0-star'
    when 20 then '1-star'
    when 40 then '2-star'
    when 60 then '3-star'
    when 80 then '4-star'
    when 100 then '5-star' end as 学生评价星级,
  case when aft.score = 100 then 'positive'
  when aft.score = 60 then 'negative' end as 标签属性,
  from_base64(af.remark)as 评论,
  aft.description_cn 标签内容,
  s2.name as 机构,
  act.type_name as 课程类型
from awj_feedbacks af
join awjcls_lesson_records alr on af.feedbackable_id = alr.id
join awjcls_lessons cl on alr.awjcls_lesson_id = cl.id and cl.state <> 6
join awj_feedback_to_tags aftt on af.id = aftt.awj_feedback_id
join awj_feedback_tags aft on aftt.awj_feedback_tag_id = aft.id
join awjcls_classes c on cl.awjcls_class_id = c.id and c.state =2
join awjcls_class_types act on c.awjcls_class_type_id = act.id
join awj_schools s1 on c.awj_school_id = s1.id
left join awj_schools s2 on s1.hq_code = s2.code and s2.id <> 71
