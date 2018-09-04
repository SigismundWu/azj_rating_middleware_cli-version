# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from copy import deepcopy
from sklearn import preprocessing


class GenTeacherStar(object):

    def __init__(self, star_rate, fa_indexs, df_wide, df_wide_final):
        self.fa_index = fa_indexs
        self.star_rate = star_rate
        self.df_wide = df_wide
        self.df_wide_final = df_wide_final

    def gen_fa_score_dataframe(self):
        fa_index = self.fa_index
        df_wide_final = self.df_wide_final
        fa_index = fa_index.as_matrix()
        df_wide_matrix = deepcopy(df_wide_final)
        df_wide_matrix.drop(['awj_teacher_id'], axis=1, inplace=True)
        df_wide_matrix = df_wide_matrix.as_matrix()
        # df_wide标准化
        df_wide_matrix = preprocessing.scale(df_wide_matrix)
        # 每个老师的各因子得分
        fa_score = np.dot(df_wide_matrix, fa_index)
        # 主成分贡献率
        var = np.array([[0.39025 / 0.87332],
                        [0.23851 / 0.87332],
                        [0.14904 / 0.87332],
                        [0.09552 / 0.87332]])
        # 每个老师的最终得分
        final_score = np.dot(fa_score, var)
        # df格式
        teacher_fa_score = np.hstack((fa_score, final_score))
        teacher_fa_score = pd.DataFrame(teacher_fa_score)
        teacher_fa_score['awj_teacher_id'] = list(df_wide_final['awj_teacher_id'])
        teacher_fa_score.rename(columns={0: 'teacher_behavior_score', 1: 'teacher_qc_score',
                                         2: 'teacher_attitude_score', 3: 'student_comment_score',
                                         4: 'final_score'}, inplace=True)
        # 去除过去一段时间周期内没上过课的老师
        teacher_fa_score = teacher_fa_score.sort_values(by='final_score', ascending=0)

        return teacher_fa_score

    def gen_star_rate(self):
        # 星级映射
        teacher_fa_score = self.gen_fa_score_dataframe()
        # 业务要求的分位数
        # 根据之前给出的格式改造那个json文件
        fixed_star_rate = dict()
        for rates in self.star_rate:
            fixed_star_rate[rates["stars"]] = rates["rate"]
        # roger的取的是quantile，就是跟业务给的百分比反过来，所以用1减业务给的百分比小数
        star_5 = teacher_fa_score['final_score'].quantile(1 - (fixed_star_rate["five_star_rate"]))
        star_4 = teacher_fa_score['final_score'].quantile(1 - (fixed_star_rate["four_star_rate"]))
        star_3 = teacher_fa_score['final_score'].quantile(1 - (fixed_star_rate["three_star_rate"]))
        star_2 = teacher_fa_score['final_score'].quantile(1 - (fixed_star_rate["two_star_rate"]))
        teacher_fa_score.loc[teacher_fa_score['final_score'] <= star_2, 'star'] = 1
        teacher_fa_score.loc[(teacher_fa_score['final_score'] > star_2) &
                             (teacher_fa_score['final_score'] <= star_3), 'star'] = 2
        teacher_fa_score.loc[(teacher_fa_score['final_score'] > star_3) &
                             (teacher_fa_score['final_score'] <= star_4), 'star'] = 3
        teacher_fa_score.loc[(teacher_fa_score['final_score'] > star_4) &
                             (teacher_fa_score['final_score'] <= star_5), 'star'] = 4
        teacher_fa_score.loc[teacher_fa_score['final_score'] > star_5, 'star'] = 5

        return teacher_fa_score

    # 把因子分析的结果（分数，星级）和原本的表进行merge
    def gen_final_table(self):
        teacher_fa_score = self.gen_star_rate()
        df_wide = self.df_wide
        teacher_fa_score = pd.merge(teacher_fa_score, df_wide[
            ['awj_teacher_id', 'normal_lesson_log_count']], on='awj_teacher_id', how='right')
        teacher_fa_score.fillna(value=0, inplace=True)
        # 应PM的要求，对最终的数值进行离差标准化处理，映射到0-5分的区间
        # 参加排序的人
        tfs_star_not_0 = teacher_fa_score[teacher_fa_score.star != 0.0]
        tfs_star_not_0_info = tfs_star_not_0.iloc[:, 5:8]  # 信息列
        tfs_star_not_0_data = tfs_star_not_0.iloc[:, 0:5]  # 数据列
        # 离差标准化
        tfs_star_not_0_data = tfs_star_not_0_data.apply(lambda x: ((x - min(x)) / (max(x) - min(x))) * 5, axis=0)
        tfs_star_not_0_data = tfs_star_not_0_data.astype(float).round(5)
        tfs_star_not_0_info = tfs_star_not_0_info.round(5)
        tfs_star_not_0_final = pd.concat([tfs_star_not_0_data, tfs_star_not_0_info], axis=1)
        # 不参加排序的人
        tfs_star_0 = teacher_fa_score[teacher_fa_score.star == 0.0]
        selected_cols = list(range(0, 5))
        selected_cols.append(7)
        tfs_star_0_null_cache = tfs_star_0.iloc[:, selected_cols].replace(0, "null")
        tfs_star_0_null_cache.insert(5, "awj_teacher_id", tfs_star_0.iloc[:, 5])
        tfs_star_0_null_cache.insert(6, "star", tfs_star_0.iloc[:, 6])
        # 最终把需要的两张整理好的表合起来
        teacher_fa_score_final = pd.concat([tfs_star_not_0_final, tfs_star_0_null_cache])

        return teacher_fa_score_final
