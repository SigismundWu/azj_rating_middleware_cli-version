# -*- coding: utf-8 -*-
import pandas as pd
import math
from azj_rating.FA_Model.PublicMethodsFAM import PublicMethodsFAM


class StudentComment(object):

    def __init__(self, df_stu_comment, class_type_name_special, hq_name_special, df_teacher_behavior_processed_cache,
                 start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.df_stu_comment = df_stu_comment
        self.class_type_name_special = class_type_name_special
        self.hq_name_special = hq_name_special
        self.df_teacher_behavior_processed_cache = df_teacher_behavior_processed_cache

    # 对原数据进行条件筛选得到需要的df
    def data_pre_processing(self):
        # 筛选条件：时间筛选条件由于筛选后数量过少，所以采用end time前的全量数据
        df_stu_comment = self.df_stu_comment.loc[(self.df_stu_comment['课程开始时间'] >= self.start_time) &
                                            (self.df_stu_comment['课程结束时间'] <= self.end_time) &
                                            (~self.df_stu_comment['机构'].isin(self.hq_name_special)) &
                                            (~self.df_stu_comment['课程类型'].isin(self.class_type_name_special))]
        # 与行为表对比，去除floater课程
        df_stu_comment = pd.merge(df_stu_comment, self.df_teacher_behavior_processed_cache,
                                  left_on=['awj_teacher_id', 'awjcls_lesson_id'],
                                  right_on=['awj_teacher_id', 'awj_lesson_id'], how='left')
        df_stu_comment = df_stu_comment.loc[~df_stu_comment['is_deleted'].isnull()]
        df_stu_comment.drop(['awj_lesson_id', 'is_deleted'], axis=1, inplace=True)
        # 天数衰减
        df_stu_comment['decay_index'] = PublicMethodsFAM().gen_decay_index(self.end_time, df_stu_comment['评价时间'])
        df_stu_comment.loc[df_stu_comment['decay_index'] < 0, 'decay_index'] = 0
        # log计算，防止0值+1;取倒数+1，防止无穷情况
        df_stu_comment['decay_index'] = df_stu_comment['decay_index'] + 2
        df_stu_comment['decay_index'] = df_stu_comment['decay_index'].apply(lambda x: math.log(x, 10))
        df_stu_comment['decay_index'] = 1 / df_stu_comment['decay_index']

        return df_stu_comment

    @staticmethod
    def good_label(df_stu_comment):
        # 正面标签统计:有时一次课有多个好评标签，导致有些老师上课次数很少，但好评标签总量超过次数本身，不公平
        # 所以此处每堂课不管有几个好评标签，都算做一个好评统计
        df_good_label = df_stu_comment.loc[df_stu_comment['学生评价星级'].isin(['5-star', '4-star'])]
        df_good_label['lesson_count_processed'] = df_good_label['lesson_count'] * df_good_label['decay_index']
        df_good_label = df_good_label.groupby(['awj_teacher_id'],
                                              as_index=False)['lesson_count_processed'].sum()
        df_good_label.rename(columns={'lesson_count_processed': 'stu_comment_log_good_behavior'}, inplace=True)

        return df_good_label

    # 提前请假的时间（单位为分钟）
    @staticmethod
    def bad_label(df_stu_comment):
        # 负面标签统计：主观原因。客观原因---产品说环境原因可能是因为是视频供应商平台或学生自己网络问题，所以不应该计入
        # 去除4星及5星的数据，理论上，四星五星无负面评价，有的都是系统bug导致
        df_bad_label = df_stu_comment.loc[~df_stu_comment['学生评价星级'].isin(['5-star', '4-star'])]
        df_bad_label['lesson_count_processed'] = df_bad_label['lesson_count'] * df_bad_label['decay_index']
        df_bad_label = df_bad_label.groupby(['awj_teacher_id'],
                                            as_index=False)['lesson_count_processed'].sum()
        df_bad_label.rename(columns={'lesson_count_processed': 'stu_comment_log_bad_behavior'}, inplace=True)

        return df_bad_label

    # 进行各种加列等运算之后后期处理
    def data_post_processing(self, df_good_label, df_bad_label):
        # merge
        df_stu_comment_res = pd.merge(df_good_label, df_bad_label, on='awj_teacher_id', how='outer')
        df_stu_comment_res['stu_comment_log_bad_behavior'].fillna(value=0, inplace=True)
        df_stu_comment_res['stu_comment_log_good_behavior'].fillna(value=0, inplace=True)
        df_stu_comment = self.data_pre_processing()

        return df_stu_comment_res, df_stu_comment
