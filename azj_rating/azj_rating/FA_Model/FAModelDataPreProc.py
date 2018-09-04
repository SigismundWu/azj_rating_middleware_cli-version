# -*- coding: utf-8 -*-
import math
import pandas as pd
from pandas.tseries.offsets import *
from azj_rating.FA_Model.ConfigurationsFAM import ConfigurationsFAM
from azj_rating.FA_Model.StudentComment import StudentComment
from azj_rating.FA_Model.TeacherQcScore import TeacherQcScore
from azj_rating.FA_Model.TeacherBehavior import TeacherBehavior


class FAModelDataPreProc(object):

    def __init__(self, path, start_time=ConfigurationsFAM().get_start_timeslot(),
                 end_time=ConfigurationsFAM().get_end_timeslot()):
        self.path = path
        self.end_time = end_time
        self.start_time = start_time
        self.class_type_name_special = ['Demo', '补课(非爱乐奇直属老师)', '托福班（30刀）', 'TOFEL',
                                        'VIP Writing/TOFEL（35刀）', 'Elite Pilot', 'Feeback Session',
                                        'New Teacher Test Class', '补课(爱乐奇直属老师)', 'Test Class',
                                        'Academic Meeting (Long)', 'Cur Experience Session-S',
                                        'Training-receiving', 'Cur Experience Session-L',
                                        'VIP Writing/TOFEL', 'Orientation Class', 'Academic Meeting',
                                        'Experience-receiving']
        self.hq_name_special = ['test']

    def get_df_teacher_monitoring(self):
        # 老师监控表
        df_teacher_monitoring = pd.read_csv(self.path + 'awj_teacher_monitoring.csv', encoding='utf-8', sep=',')
        # 因对生产环境中的nan值
        df_teacher_monitoring.dropna(subset=["awj_teacher_id"], inplace=True)
        # dtypes
        df_teacher_monitoring['awj_teacher_id'] = df_teacher_monitoring['awj_teacher_id'].astype('int')
        df_teacher_monitoring['created_at'] = pd.to_datetime(df_teacher_monitoring['created_at'])
        # drop duplicates
        df_teacher_monitoring.drop_duplicates(
            subset=list(df_teacher_monitoring.columns), keep='first', inplace=True)
        # sort
        df_teacher_monitoring = df_teacher_monitoring.sort_values(
            by=['awj_teacher_id', 'awjcls_lesson_id', 'created_at'], ascending=[1, 1, 1])
        # 该表只取abnormal_type为4，5的行，分别表示zoom崩溃和课件崩溃，非老师原因
        df_teacher_monitoring = df_teacher_monitoring.loc[
            df_teacher_monitoring['abnormal_type'].isin([4, 5])]
        df_teacher_monitoring = df_teacher_monitoring.groupby(
            ['awj_teacher_id', 'awjcls_lesson_id', 'abnormal_type'], as_index=False).last()

        return df_teacher_monitoring

    def get_df_qc(self):
        # 老师QC明细表
        df_qc = pd.read_csv(self.path + '老师qc明细.csv', encoding='utf-8', sep=',')
        df_qc.dropna(subset=["awj_teacher_id"], inplace=True)
        # dtypes
        df_qc['awj_teacher_id'] = df_qc['awj_teacher_id'].astype('int')
        df_qc['score_recorded_at'] = pd.to_datetime(df_qc['score_recorded_at'])
        df_qc['assigned_at'] = pd.to_datetime(df_qc['assigned_at'])
        df_qc['start_time'] = pd.to_datetime(df_qc['start_time'])
        df_qc['end_time'] = pd.to_datetime(df_qc['end_time'])
        # drop duplicates-老师同一堂课有时会有多次qc，check后发现分数都一样，所以去重时按照以下字段去重即可
        columns = ['awj_teacher_id', 'awjcls_lesson_id', 'score']
        df_qc.drop_duplicates(subset=columns, keep='last', inplace=True)
        # sort
        df_qc = df_qc.sort_values(by=['awj_teacher_id', 'start_time'], ascending=[1, 1])

        return df_qc

    def get_df_teacher_behavior(self):
        # 老师行为表
        df_teacher_behavior = pd.read_csv(self.path + '老师行为信息明细.csv', sep=',', encoding='utf-8')
        df_teacher_behavior.dropna(subset=["awj_teacher_id"], inplace=True)
        # 老师监控表
        df_teacher_monitoring = self.get_df_teacher_monitoring()        # dtypes
        df_teacher_behavior['awj_teacher_id'] = df_teacher_behavior['awj_teacher_id'].astype('int')
        df_teacher_behavior['start_time'] = pd.to_datetime(df_teacher_behavior['start_time'])
        df_teacher_behavior['end_time'] = pd.to_datetime(df_teacher_behavior['end_time'])
        df_teacher_behavior['actual_start_time'] = pd.to_datetime(df_teacher_behavior['actual_start_time'])
        df_teacher_behavior['actual_end_time'] = pd.to_datetime(df_teacher_behavior['actual_end_time'])
        df_teacher_behavior.drop_duplicates(subset=list(df_teacher_behavior.columns), inplace=True)
        # sort
        df_teacher_behavior = df_teacher_behavior.sort_values(by=[
            'awj_teacher_id', 'awj_lesson_id', 'start_time', 'teacher_status_for_lesson'], ascending=[1, 1, 1, 1])
        # 老师id加lesson_id应该唯一，但有时有重复情况，因为有些老师先请了假，后来又来上课了，所以请假应该去除
        df_teacher_behavior = df_teacher_behavior.groupby(
            ['awj_teacher_id', 'awj_lesson_id'], as_index=False).last()
        # 与monitoring表对比，去除老师abnormal_lesson细分为4，5状态下的课程记录
        df_teacher_behavior = pd.merge(df_teacher_behavior,
                                       df_teacher_monitoring[['awj_teacher_id', 'awjcls_lesson_id', 'abnormal_type']],
                                       left_on=['awj_teacher_id', 'awj_lesson_id'],
                                       right_on=['awj_teacher_id', 'awjcls_lesson_id'], how='left')
        index = df_teacher_behavior.loc[
            (df_teacher_behavior['teacher_status_for_lesson'] == 'abnormal_lesson') &
            (df_teacher_behavior['abnormal_type'].isin([4, 5]))].index
        df_teacher_behavior = df_teacher_behavior.loc[~df_teacher_behavior.index.isin(list(index))]
        df_teacher_behavior.drop(['awjcls_lesson_id', 'abnormal_type'], axis=1, inplace=True)

        return df_teacher_behavior

    def get_df_teacher_info(self):
        # 老师信息表
        df_teacher_info = pd.read_csv(self.path + '老师基本信息.csv', sep=',', encoding='utf-8')
        df_teacher_info.dropna(subset=["awj_teacher_id"], inplace=True)
        # dtypes
        df_teacher_info['awj_teacher_id'] = df_teacher_info['awj_teacher_id'].astype(int)
        df_teacher_info['创建时间'] = pd.to_datetime(df_teacher_info['创建时间'])
        df_teacher_info['首次上架时间'] = pd.to_datetime(df_teacher_info['首次上架时间'])
        df_teacher_info['首课时间'] = pd.to_datetime(df_teacher_info['首课时间'])
        df_teacher_info.drop_duplicates(
            subset=list(df_teacher_info.columns), keep='first', inplace=True)
        # 根据业务要求只取某些type类型老师，其他去除
        df_teacher_info = df_teacher_info.loc[df_teacher_info['teacher_type'].isin([
            'booking&arrangement', 'arrangement_only', 'booking_only'])]
        # sort
        df_teacher_info = df_teacher_info.sort_values(by=['awj_teacher_id'], ascending=[1])
        df_teacher_info = df_teacher_info[['awj_teacher_id', 'state', '创建时间',
                                           '首次上架时间', '首课时间']]

        return df_teacher_info

    def get_df_stu_comment(self):
        # 学生评价明细表
        df_stu_comment = pd.read_csv(self.path + '学生评价明细.csv', sep=',', encoding='utf-8')
        df_stu_comment.dropna(subset=["awj_teacher_id"], inplace=True)
        # dtypes
        df_stu_comment['awj_teacher_id'] = df_stu_comment['awj_teacher_id'].astype(int)
        df_stu_comment['学生评价星级'] = df_stu_comment['学生评价星级'].astype('str')
        df_stu_comment = df_stu_comment.loc[df_stu_comment['学生评价星级'].isin(['1-star', '2-star',
                                                                           '3-star', '4-star', '5-star'])]
        df_stu_comment['评价时间'] = pd.to_datetime(df_stu_comment['评价时间'])
        df_stu_comment['课程开始时间'] = pd.to_datetime(df_stu_comment['课程开始时间'])
        df_stu_comment['课程结束时间'] = pd.to_datetime(df_stu_comment['课程结束时间'])
        df_stu_comment.drop_duplicates(subset=list(df_stu_comment.columns), keep='first', inplace=True)
        # sort
        df_stu_comment = df_stu_comment.sort_values(by=[
            'awj_teacher_id', '评价时间'], ascending=[1, 1])
        # 此处仍然算一次，两次效果非常差
        df_stu_comment['lesson_count'] = 1
        df_stu_comment = df_stu_comment.groupby(['评价id'], as_index=False).last()

        return df_stu_comment

    def process_df_qc(self, df_qc):
        # 函数调用
        qc_obj = TeacherQcScore(
            df_qc, self.class_type_name_special, self.hq_name_special,
            self.start_time, self.end_time,
        )

        df_qc = qc_obj.data_pre_processing()
        df_qc_res = qc_obj.data_post_processing(df_qc)

        return df_qc_res

    def process_df_teacher_behavior(self, df_teacher_behavior):
        tb_obj = TeacherBehavior(
            df_teacher_behavior, self.class_type_name_special, self.hq_name_special,
            self.start_time, self.end_time,
        )

        df_tb = tb_obj.data_pre_processing()
        df_clt = tb_obj.count_lesson_types(df_tb)
        df_aflam = tb_obj.ask_for_leave_advanced_minutes(df_tb)
        # df_teacher_behavior_processed用途只是占位，因此不返回
        df_teacher_behavior_res, df_teacher_behavior_processed = tb_obj.data_post_processing(df_clt, df_aflam)

        return df_teacher_behavior_res

    def process_df_teacher_behavior_cache(self, df_teacher_behavior):
        # 学生评价表中有些课程是floater的课程，需要与行为表课程对比删除（行为表无该情况）
        # df_teacher_behavior_res_cache只是占位用，因此不在这个函数里面返回
        tb_cache_obj = TeacherBehavior(
            df_teacher_behavior, self.class_type_name_special, self.hq_name_special,
            self.start_time - DateOffset(years=5), self.end_time,
        )
        # df_teacher_behavior_res_cache用途只是占位，因此不返回
        df_tb = tb_cache_obj.data_pre_processing()
        df_clt = tb_cache_obj.count_lesson_types(df_tb)
        df_aflam = tb_cache_obj.ask_for_leave_advanced_minutes(df_tb)

        df_teacher_behavior_res_cache, df_teacher_behavior_processed_cache = tb_cache_obj.data_post_processing(
            df_clt, df_aflam
        )

        df_teacher_behavior_processed_cache = df_teacher_behavior_processed_cache[['awj_teacher_id', 'awj_lesson_id']]
        df_teacher_behavior_processed_cache['is_deleted'] = 'no'

        return df_teacher_behavior_processed_cache

    def process_df_stu_comment(self, df_stu_comment, df_teacher_behavior_processed_cache):
        stuc_obj = StudentComment(
            df_stu_comment, self.class_type_name_special, self.hq_name_special,
            df_teacher_behavior_processed_cache, self.start_time, self.end_time,
        )

        df_stu_comment = stuc_obj.data_pre_processing()
        df_gl = stuc_obj.good_label(df_stu_comment)
        df_bl = stuc_obj.bad_label(df_stu_comment)
        # df_stu_comment_check只是用于制作查询表的，在这个功能中是占位参数，但是以后是否有用未知，暂时保留
        df_stu_comment_res, df_stu_comment_check = stuc_obj.data_post_processing(df_gl, df_bl)

        return df_stu_comment_res

    def gen_df_wide_prototype(self):
        # 宽表
        df_teacher_info = self.get_df_teacher_info()
        df_teacher_behavior = self.get_df_teacher_behavior()
        df_teacher_behavior_res = self.process_df_teacher_behavior(df_teacher_behavior)
        df_teacher_behavior_res_cache = self.process_df_teacher_behavior_cache(df_teacher_behavior)
        df_qc = self.get_df_qc()
        df_qc_res = self.process_df_qc(df_qc)
        df_stu_comment = self.get_df_stu_comment()
        df_stu_comment_res = self.process_df_stu_comment(df_stu_comment, df_teacher_behavior_res_cache)

        df_wide = pd.merge(df_teacher_info, df_teacher_behavior_res, on='awj_teacher_id', how='left')
        df_wide = pd.merge(df_wide, df_qc_res, on='awj_teacher_id', how='left')
        df_wide = pd.merge(df_wide, df_stu_comment_res, on='awj_teacher_id', how='left')

        # 有些老师3个月内可能无qc分数，所以取历史qc记录处理后填补0分情况
        qc_all_obj = TeacherQcScore(df_qc, self.class_type_name_special, self.hq_name_special,
                                    self.start_time - DateOffset(years=5), self.end_time)
        df_qc_all = qc_all_obj.data_post_processing(qc_all_obj.data_pre_processing())

        df_qc_all = df_qc_all[['awj_teacher_id', 'teacher_score_max', 'teacher_score_min', 'log_decay_score_mean']]
        df_qc_all.rename(columns={'teacher_score_max': 'teacher_score_max_all',
                                  'teacher_score_min': 'teacher_score_min_all',
                                  'log_decay_score_mean': 'log_decay_score_mean_all'}, inplace=True)
        df_wide = pd.merge(df_wide, df_qc_all, on='awj_teacher_id', how='left')
        # 有些老师没上过课，但请过假，此处为了让这些老师参加评分而非直接三星，所以将normal_lesson_log_count平滑处理
        df_wide.loc[(df_wide['normal_lesson_log_count'] == 0) &
                    (df_wide['ask_for_leave_log_count'] > 0), 'normal_lesson_log_count'] = math.log(2, 10)

        return df_wide

    def gen_df_wide_final(self):
        # 衍生新字段
        df_wide = self.gen_df_wide_prototype()
        df_wide['log_ask_for_leave/log_normal_lesson'] = (
                df_wide['ask_for_leave_log_count'] /
                df_wide['normal_lesson_log_count']
        )
        df_wide['abnormal_all_log_count'] = (
                df_wide['no_show_lesson_log_count'] + df_wide['late_lesson_log_count'] +
                df_wide['abnormal_lesson_log_count'] + df_wide['ask_for_leave_log_count']
        )
        df_wide['abnormal_all_log_percent'] = (df_wide['abnormal_all_log_count']) / (
                df_wide['normal_lesson_log_count'] + df_wide['abnormal_all_log_count']
        )
        df_wide['lesson_time_range'] = ((self.end_time - df_wide['首课时间']).dt.total_seconds()) / (3600 * 24)
        df_wide.loc[df_wide['lesson_time_range'] == 0,
                    'lesson_time_range'] = ((self.end_time - df_wide['创建时间']).dt.total_seconds()) / (3600 * 24)

        return df_wide
