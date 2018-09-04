# -*- coding: utf-8 -*-
import unittest
import pandas as pd
import warnings
import datetime
from azj_rating.FA_Model.StudentComment import StudentComment
from azj_rating.FA_Model.FAModelDataPreProc import FAModelDataPreProc


class TestStudentComment(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore")  # 在setup里面初始化指定忽略掉警告
        path = "./tests/examples_FAM/df_sc_data/"
        end_time = datetime.datetime(2018, 4, 30, 23, 59, 59)
        start_time = datetime.datetime(2018, 1, 30, 23, 59, 59)
        class_type_name_special = ['Demo', '补课(非爱乐奇直属老师)', '托福班（30刀）', 'TOFEL',  # 筛选课程
                                   'VIP Writing/TOFEL（35刀）', 'Elite Pilot', 'Feeback Session',
                                   'New Teacher Test Class', '补课(爱乐奇直属老师)', 'Test Class',
                                   'Academic Meeting (Long)', 'Cur Experience Session-S',
                                   'Training-receiving', 'Cur Experience Session-L',
                                   'VIP Writing/TOFEL', 'Orientation Class', 'Academic Meeting',
                                   'Experience-receiving']
        hq_name_special = ['test']
        origin_path = "./tests/examples_FAM/data_pre_proc/"
        data_pre_proc_obj = FAModelDataPreProc(origin_path, start_time, end_time)
        # 学生评价明细表
        df_stu_comment = data_pre_proc_obj.get_df_stu_comment()
        # 获取教师行为数据cache版
        df_teacher_behavior = data_pre_proc_obj.get_df_teacher_behavior()
        df_teacher_behavior_processed_cache = data_pre_proc_obj.process_df_teacher_behavior_cache(df_teacher_behavior)

        self.sc_obj = StudentComment(df_stu_comment, class_type_name_special, hq_name_special,
                                     df_teacher_behavior_processed_cache, start_time, end_time)
        self.data_pre_processing_res = pd.read_csv(path + "sc_data_pre_process_res.csv", encoding="utf-8", float_precision="high")
        self.good_label_res = pd.read_csv(path + "sc_good_label_res.csv", encoding="utf-8", float_precision="high")
        self.bad_label_res = pd.read_csv(path + "sc_bad_label_res.csv", encoding="utf-8", float_precision="high")
        self.df_sc_test_result = pd.read_csv(path + "df_stu_comment_test_result.csv", encoding="utf-8", float_precision="high")

    def tearDown(self):
        pass

    def test_data_pre_processing(self):
        processed_data = self.sc_obj.data_pre_processing()
        processed_data.reset_index(drop=True, inplace=True)
        # 强制round，与测试数据保持小数点数量一致
        processed_data = processed_data.round(5)
        processed_data = processed_data.astype(str)
        processed_data = processed_data.replace("NaT", "nan")  # 存在时间序列数据的空值为NaT的问题，在测试中替换，不影响实际使用
        # 测试对象被读进来的小数是16位的，而在函数里面产生的小数是17位
        # json格式最多15位，dict同理，因此读取进来之后会有小数位数不同的问题引发的错误，强制round
        res_data = self.data_pre_processing_res.round(5)
        res_data = res_data.astype(str)
        res_data = res_data.to_dict()
        self.assertDictEqual(
            processed_data.to_dict(),
            res_data
        )

    def test_good_label(self):
        processed_data = self.sc_obj.good_label(self.sc_obj.data_pre_processing())
        processed_data = processed_data.round(5)
        processed_data = processed_data.to_json()
        res_data = self.good_label_res.to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_bad_label(self):
        processed_data = self.sc_obj.bad_label(self.sc_obj.data_pre_processing())
        processed_data = processed_data.round(5)
        processed_data = processed_data.to_json()
        res_data = self.bad_label_res
        res_data = res_data.to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_data_post_processing(self):
        df_good_label = self.sc_obj.good_label(self.sc_obj.data_pre_processing())
        df_bad_label = self.sc_obj.bad_label(self.sc_obj.data_pre_processing())
        # 这个函数返回了两个值，其中第一个值等于第一个test的值（根据roger的源码结构）
        processed_data, tmp_data = self.sc_obj.data_post_processing(df_good_label, df_bad_label)
        processed_data = processed_data.round(5)
        processed_data = processed_data.astype(str)
        processed_data = processed_data.to_json()
        res_data = self.df_sc_test_result
        res_data = res_data.astype(str)
        res_data = res_data.to_json()
        self.assertEqual(
            processed_data,
            res_data
        )
