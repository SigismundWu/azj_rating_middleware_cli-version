SELECT t1.id as awj_teacher_id,
  case t1.state when 0 then 'oboard'
    when 1 then 'active'
    when 2 then 'deactive' end as state,
  case  t.ethnicity when 0 then 'unspecified'
    when 1 then 'white'
      when 2 then 'black'
        when 3 then 'brown'
          when 4 then 'east_asian'
            when 5 then 'other' end as ethnicity,
  case t.teacher_type when 0 then 'booking&arrangement'
    when 1 then 'arrangement_only'
    when 2 then 'booking_only'
    when 3 then 'arrangement&booking_floater'
    when 4 then 'arrangement_only_floater'
      when 5 then 'customer_support' end as teacher_type,
  t1.gender,
  t1.refered_by,
  t1.created_at as 创建时间,
  t4.首次上架时间,
  t1.first_lesson_time as 首课时间,
   t3.country, t3.timezone,
  t3.years_of_expericence,
  t3.degree_and_university,
  t3.certification,
  t3.child_exp,
  t3.teaching_exp,
  t3.testing_exp,
  t3.tutoring_exp,
  t.can_auto_assign,
  t.can_race_class,
  t.access_to_online_courseware from (
SELECT
  t.id,
  CONCAT_WS(' ', t.first_name, t.last_name) AS name,
  t.state,
  rt.refered_by,
  case tpusers.gender when 1 then 'male' when 2 then 'female' else 'unknown' end as gender,
  t.created_at,
  datediff(now(), t.created_at) as 'days from create date',
  tmp.start_time as first_lesson_time,
  datediff(now(), tmp.start_time) as 'days from first lesson date',
  lessons.lesson_count
FROM awj_teachers t
LEFT join tpusers on tpusers.id = t.tpuser_id
LEFT join recruitment_teachers rt on rt.id = t.recruitment_teacher_id
  LEFT JOIN
  (SELECT
     l.awj_teacher_id,
     min(l.start_time) AS start_time
   FROM awjcls_lessons l
     INNER JOIN awjcls_classes c
       ON c.id = l.awjcls_class_id
     INNER JOIN
     awj_schools s1 ON c.awj_school_id = s1.id
     LEFT JOIN
     awj_schools s2 ON s1.hq_code = s2.code
   WHERE l.state != 6 AND s2.formal_hq_school = TRUE
         AND c.state = 2
   GROUP BY l.awj_teacher_id) tmp
    ON t.id = tmp.awj_teacher_id
    LEFT JOIN
  (SELECT
     l.awj_teacher_id,
     count(1) as lesson_count
   FROM awjcls_lessons l
     INNER JOIN awjcls_classes c
       ON c.id = l.awjcls_class_id
     INNER JOIN
     awj_schools s1 ON c.awj_school_id = s1.id
     LEFT JOIN
     awj_schools s2 ON s1.hq_code = s2.code
   WHERE l.state != 6 AND s2.formal_hq_school = TRUE
         AND c.state = 2
         AND l.start_time < now()
   GROUP BY l.awj_teacher_id) lessons
    ON t.id = lessons.awj_teacher_id
WHERE t.organization = 'pdd') t1
left join
(
SELECT
  t.id,
  CONCAT_WS(' ', t.first_name, t.last_name) AS name,
  t.country,
  t.timezone,
  years_of_expericence,
  -- (case
  -- when ethnicity = 0 then 'unspecified'
  -- when ethnicity = 1 then 'white'
  -- when ethnicity = 2 then 'black'
  -- when ethnicity = 3 then 'brown'
  -- when ethnicity = 4 then 'east_asian'
  -- when ethnicity = 5 then 'other'
  -- end) as 'Ethnicity',
  red.degree_and_university,
  rex_cer.certification,
  rex_child.child_exp,
  rex_teaching.teaching_exp,
  rex_testing.testing_exp,
  rex_tutoring.tutoring_exp
FROM awj_teachers t
  LEFT JOIN recruitment_teachers rt ON rt.id = t.recruitment_teacher_id
  LEFT JOIN (
              SELECT
                teacher_id,
                group_concat(concat_ws(', ', (CASE
                                              WHEN academic_degree = 0
                                                THEN 'phd'
                                              WHEN academic_degree = 1
                                                THEN 'phd_student'
                                              WHEN academic_degree = 2
                                                THEN 'master'
                                              WHEN academic_degree = 3
                                                THEN 'master_student'
                                              WHEN academic_degree = 4
                                                THEN 'bachelor'
                                              WHEN academic_degree = 5
                                                THEN 'bachelor_student'
                                              WHEN academic_degree = 10
                                                THEN 'associate'
                                              WHEN academic_degree = 6
                                                THEN 'none_of_above'
                                              ELSE 'None'
                                              END), university) SEPARATOR '; ') AS degree_and_university
              FROM recruitment_educations
              GROUP BY teacher_id) red ON red.teacher_id = rt.id
  LEFT JOIN (
              SELECT
                teacher_id,
                group_concat(concat_ws(', ', (CASE
                                              WHEN category = 0
                                                THEN 'TEFL'
                                              WHEN category = 1
                                                THEN 'TESOL'
                                              WHEN category = 2
                                                THEN 'CELTA'
                                              WHEN category = 3
                                                THEN 'TKT'
                                              WHEN category = 4
                                                THEN 'Other'
                                              ELSE 'None'
                                              END), duration) SEPARATOR '; ') AS certification
              FROM recruitment_experiences
              WHERE type = 'Recruitment::Certification'
              GROUP BY teacher_id) rex_cer ON rex_cer.teacher_id = rt.id
    LEFT JOIN (
              SELECT
                teacher_id,
                group_concat(concat_ws(', ', (CASE
                                              WHEN category = 0
                                                THEN 'Camps'
                                              WHEN category = 1
                                                THEN 'Day Care'
                                              WHEN category = 2
                                                THEN 'Baby Sitting'
                                              WHEN category = 3
                                                THEN 'Sports Coaching'
                                              WHEN category = 4
                                                THEN 'Other'
                                              ELSE 'None'
                                              END), duration) SEPARATOR '; ') AS child_exp
              FROM recruitment_experiences
              WHERE type = 'Recruitment::ChildrenExperience'
              GROUP BY teacher_id) rex_child ON rex_child.teacher_id = rt.id
      LEFT JOIN (
              SELECT
                teacher_id,
                group_concat(concat_ws(', ', (CASE
                                              WHEN category = 0
                                                THEN 'Pre-school'
                                              WHEN category = 1
                                                THEN 'K-6'
                                              WHEN category = 2
                                                THEN '7_12'
                                              WHEN category = 3
                                                THEN 'College'
                                              WHEN category = 4
                                                THEN 'Other'
                                              ELSE 'None'
                                              END), duration) SEPARATOR '; ') AS teaching_exp
              FROM recruitment_experiences
              WHERE type = 'Recruitment::TeachingExperience'
              GROUP BY teacher_id) rex_teaching ON rex_teaching.teacher_id = rt.id
        LEFT JOIN (
              SELECT
                teacher_id,
                group_concat(concat_ws(', ', (CASE
                                              WHEN category = 0
                                                THEN 'TOFEL'
                                              WHEN category = 1
                                                THEN 'IELTS'
                                              WHEN category = 2
                                                THEN 'SAT'
                                              WHEN category = 3
                                                THEN 'ISEE'
                                              WHEN category = 4
                                                THEN 'Other'
                                              ELSE 'None'
                                              END), duration) SEPARATOR '; ') AS testing_exp
              FROM recruitment_experiences
              WHERE type = 'Recruitment::TestingTutorExperience'
              GROUP BY teacher_id) rex_testing ON rex_testing.teacher_id = rt.id
          LEFT JOIN (
              SELECT
                teacher_id,
                group_concat(concat_ws(', ', (CASE
                                              WHEN category = 0
                                                THEN 'Pre-school'
                                              WHEN category = 1
                                                THEN 'K-6'
                                              WHEN category = 2
                                                THEN '7_12'
                                              WHEN category = 3
                                                THEN 'College'
                                              WHEN category = 4
                                                THEN 'Other'
                                              ELSE 'None'
                                              END), duration) SEPARATOR '; ') AS tutoring_exp
              FROM recruitment_experiences
              WHERE type = 'Recruitment::TutoringExperience'
              GROUP BY teacher_id) rex_tutoring ON rex_tutoring.teacher_id = rt.id
WHERE state = 1 AND organization = 'pdd'
ORDER BY t.id DESC
) t3 on t1.id = t3.id
join
  (select t.id, concat_ws(' ', first_name, last_name) as name, country, t.state, tpu.email,
-- 首次上架时间，在功能上线后创建的老师才正确。否则是功能上线后第一次被操作上架的时间。
  CASE WHEN t.created_at >= '2017-06-01'
    THEN onboard.first_onboard_date
  ELSE t.created_at END                           AS 首次上架时间
from awj_teachers t left join tpusers tpu on t.tpuser_id = tpu.id
LEFT JOIN (SELECT
               to1.awj_teacher_id,
               to1.created_at AS first_onboard_date
             FROM awj_teacher_operations to1
               LEFT JOIN awj_teacher_operations to2
                 ON to2.operation_type = 1 AND to1.awj_teacher_id = to2.awj_teacher_id AND
                    to1.created_at > to2.created_at
             WHERE to1.operation_type = 1 AND to2.id IS NULL
             GROUP BY to1.awj_teacher_id
             ORDER BY to1.created_at) onboard ON onboard.awj_teacher_id = t.id
where organization = 'pdd' and is_virtual = 0
group by t.id)t4 on t1.id = t4.id
join awj_teachers t on t1.id = t.id  and t.is_virtual = 0 and t.organization = 'PDD'