# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import math
from azj_rating.FA_Model.PublicMethodsFAM import PublicMethodsFAM


class TeacherBehavior(object):

    def __init__(self, df_teacher_behavior, class_type_name_special, hq_name_special, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.df_teacher_behavior = df_teacher_behavior
        self.class_type_name_special = class_type_name_special
        self.hq_name_special = hq_name_special

    # 对原数据进行条件筛选得到需要的df
    def data_pre_processing(self):
        df_teacher_behavior_p = self.df_teacher_behavior
        df_teacher_behavior_p = df_teacher_behavior_p.loc[
            (~df_teacher_behavior_p['上课类型'].isin(self.class_type_name_special)) &
            (~df_teacher_behavior_p['机构'].isin(self.hq_name_special)) &
            (df_teacher_behavior_p['start_time'] >= self.start_time) &
            (df_teacher_behavior_p['end_time'] <= self.end_time) &
            (~df_teacher_behavior_p['teacher_status_for_lesson'].isin(['system_failure']))]
        # 预处理
        # 对老师关于课的处理，以最小slot为准，一般是半小时，因此被除的应该是3600 * 2
        minimum_time_slot = 3600 / 2
        # 分钟转换为天，该列数据原始数据以分钟为单位
        day_to_minute = 60 * 24
        # 平滑系数，加2是为了比1更贴近实际数值
        smooth_coefficient = 2
        df_teacher_behavior_p['lesson_count'] = (((df_teacher_behavior_p['end_time'] -
                                                 df_teacher_behavior_p['start_time']).dt.total_seconds()) /
                                                 minimum_time_slot)
        df_teacher_behavior_p.loc[df_teacher_behavior_p['teacher_status_for_lesson'] == 'no_show',
                                  'ask_for_leave_advanced_minutes'] = 0
        df_teacher_behavior_p['ask_for_leave_advanced_days'] = (df_teacher_behavior_p['ask_for_leave_advanced_minutes'] /
                                                                day_to_minute)
        # 天数衰减
        df_teacher_behavior_p['decay_index'] = PublicMethodsFAM().gen_decay_index(
            self.end_time, df_teacher_behavior_p['start_time']
        )

        df_teacher_behavior_p.loc[df_teacher_behavior_p['decay_index'] < 0, 'decay_index'] = 0
        # log计算，防止0值+1;取倒数+1，防止无穷情况
        df_teacher_behavior_p['decay_index'] = df_teacher_behavior_p['decay_index'] + smooth_coefficient
        df_teacher_behavior_p['decay_index'] = df_teacher_behavior_p['decay_index'].apply(lambda x: math.log(x, 10))
        # 取倒数
        df_teacher_behavior_p['decay_index'] = 1 / df_teacher_behavior_p['decay_index']

        return df_teacher_behavior_p

    @staticmethod
    def count_lesson_types(df_teacher_behavior):
        # count lesson types
        df_teacher_behavior_res = df_teacher_behavior[['awj_teacher_id']]
        df_teacher_behavior_res.drop_duplicates(keep='first', inplace=True)
        types = ['normal_lesson', 'late', 'no_show', 'abnormal_lesson', 'ask_for_leave']
        for itm in types:
            df_count = df_teacher_behavior.loc[
                df_teacher_behavior['teacher_status_for_lesson'].isin([itm])]
            df_count['log_lesson_count'] = df_count['lesson_count'] * df_count['decay_index']
            df_count = df_count.groupby(
                ['awj_teacher_id'], as_index=False)['log_lesson_count'].sum()
            df_count.reset_index()
            if (itm.find('ask_for_leave') > -1) | (itm.find('lesson') > -1):
                df_count.rename(columns={'log_lesson_count': itm + '_log_count'}, inplace=True)
            else:
                df_count.rename(columns={'log_lesson_count': itm + '_lesson_log_count'}, inplace=True)
            df_teacher_behavior_res = pd.merge(df_teacher_behavior_res, df_count,
                                               on='awj_teacher_id', how='left')

        return df_teacher_behavior_res

    # 提前请假的时间（单位为分钟）
    @staticmethod
    def ask_for_leave_advanced_minutes(df_teacher_behavior):
        df_advanced_days = df_teacher_behavior.loc[
            df_teacher_behavior['teacher_status_for_lesson'].isin(['ask_for_leave', 'no_show'])]
        df_advanced_days['ask_for_leave_advanced_log_days'] = df_advanced_days['decay_index'] * df_advanced_days[
            'ask_for_leave_advanced_days']
        # 求均值
        df_advanced_days_mean = df_advanced_days.groupby(['awj_teacher_id'], as_index=False).agg(
            {'ask_for_leave_advanced_log_days': np.sum, 'decay_index': np.sum})
        df_advanced_days_mean.reset_index(inplace=True)
        df_advanced_days_mean['advanced_days_log_mean'] = (df_advanced_days_mean['ask_for_leave_advanced_log_days'] /
                                                           df_advanced_days_mean['decay_index'])
        df_advanced_days_mean = df_advanced_days_mean[['awj_teacher_id', 'advanced_days_log_mean']]
        # 求最大最小值及方差
        df_advanced_days_others = df_advanced_days.groupby(['awj_teacher_id'],
                                                           as_index=False)['ask_for_leave_advanced_days'].agg(
            ['min', 'max', 'std'])
        df_advanced_days_others.reset_index(inplace=True)
        df_advanced_days_others.loc[df_advanced_days_others['std'].isnull(),
                                    'std'] = df_advanced_days_others['std'].mean()
        df_advanced_days_others.rename(columns={'min': 'advanced_days_min',
                                                'max': 'advanced_days_max', 'std': 'advanced_days_std'}, inplace=True)
        df_advanced_days = pd.merge(df_advanced_days_mean, df_advanced_days_others,
                                    on='awj_teacher_id', how='left')

        return df_advanced_days

    # 进行各种加列等运算之后后期处理
    def data_post_processing(self, df_teacher_behavior_res, df_advanced_days):
        df_teacher_behavior_res_f = pd.merge(df_teacher_behavior_res, df_advanced_days,
                                             on='awj_teacher_id', how='left')
        columns = ['normal_lesson_log_count', 'late_lesson_log_count', 'no_show_lesson_log_count',
                   'abnormal_lesson_log_count', 'ask_for_leave_log_count', 'advanced_days_log_mean',
                   'advanced_days_min', 'advanced_days_max', 'advanced_days_std']
        for itm in columns:
            df_teacher_behavior_res_f[itm].fillna(value=0, inplace=True)

        df_teacher_behavior_f = self.data_pre_processing()

        return df_teacher_behavior_res_f, df_teacher_behavior_f
