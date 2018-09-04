# -*- coding: utf-8 -*-
import math
import numpy as np
import pandas as pd
from azj_rating.FA_Model.PublicMethodsFAM import PublicMethodsFAM


class TeacherQcScore(object):

    def __init__(self, df_qc, class_type_name_special, hq_name_special, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.class_type_name_special = class_type_name_special
        self.hq_name_special = hq_name_special
        self.df_qc = df_qc

    # 条件筛选，按条件生成一个需要的df
    def data_pre_processing(self):
        # 筛选条件
        smooth_coefficient = 2
        df_qc = self.df_qc.loc[(~self.df_qc['class_type_name'].isin(self.class_type_name_special)) &
                               (~self.df_qc['hq_name'].isin(self.hq_name_special)) &
                               (self.df_qc['start_time'] >= self.start_time) & (self.df_qc['end_time'] <= self.end_time)]
        # log score-mean
        df_qc['decay_index'] = PublicMethodsFAM().gen_decay_index(self.end_time, df_qc['score_recorded_at'])
        df_qc.loc[df_qc['decay_index'] < 0, 'decay_index'] = 0  # qc时间有时会在end_time之后造成负值
        df_qc['decay_index'] = df_qc['decay_index'] + smooth_coefficient  # log计算，防止0值+1;取倒数+1，防止无穷情况
        df_qc['decay_index'] = df_qc['decay_index'].apply(lambda x: math.log(x, 10))
        df_qc['decay_index'] = 1 / df_qc['decay_index']
        df_qc['log_decay_score'] = df_qc['score'] * df_qc['decay_index']

        return df_qc

    # log score-mean，计算log_score_mean的df
    @staticmethod
    def cal_log_score_mean(df_qc):
        df_teacher_log_score = df_qc.groupby(
            ['awj_teacher_id'], as_index=False).agg(
            {'log_decay_score': np.sum, 'decay_index': np.sum}
        )
        df_teacher_log_score['log_decay_score_mean'] = (df_teacher_log_score['log_decay_score'] /
                                                        df_teacher_log_score['decay_index'])
        df_teacher_log_score = df_teacher_log_score[['awj_teacher_id', 'log_decay_score_mean']]

        return df_teacher_log_score

    # 计算分数和标准误的df
    @staticmethod
    def cal_std_missing(df_qc):
        df_teacher_score = df_qc.groupby(
            ['awj_teacher_id'], as_index=False)['score'].agg(
            ['max', 'min', 'count', np.std]
        )
        df_teacher_score.loc[df_teacher_score['std'].isnull(), 'std'] = df_teacher_score['std'].mean()
        df_teacher_score.rename(columns={'max': 'teacher_score_max', 'min': 'teacher_score_min',
                                         'count': 'teacher_qc_count', 'std': 'teacher_score_std'}, inplace=True)
        df_teacher_score.reset_index(inplace=True)

        return df_teacher_score

    # df合成，输出最终的Qc分数数据框
    def data_post_processing(self, df_qc):
        df_teacher_log_score = self.cal_log_score_mean(df_qc)
        df_teacher_score = self.cal_std_missing(df_qc)

        df_qc_res = pd.merge(df_teacher_score, df_teacher_log_score, on="awj_teacher_id", how="left")

        return df_qc_res
