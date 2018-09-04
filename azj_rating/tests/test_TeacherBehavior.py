# -*- coding: utf-8 -*-
import unittest
import pandas as pd
import warnings
import datetime
from azj_rating.FA_Model.TeacherBehavior import TeacherBehavior
from azj_rating.FA_Model.FAModelDataPreProc import FAModelDataPreProc


class TestTeacherBehavior(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore")  # 在setup里面初始化指定忽略掉警告
        path = "./tests/examples_FAM/df_tb_data/"
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
        df_teacher_behavior = data_pre_proc_obj.get_df_teacher_behavior()

        self.tb_obj = TeacherBehavior(df_teacher_behavior, class_type_name_special, hq_name_special, start_time, end_time)
        self.data_pre_processing_res = pd.read_csv(path + "tb_data_pre_proc_res.csv", encoding="utf-8", float_precision="high")
        self.count_lesson_types_res = pd.read_csv(path + "tb_count_lesson_types_res.csv", encoding="utf-8", float_precision="high")
        self.AFLAM_res = pd.read_csv(path + "tb_ask_for_leave_advanced_minutes_res.csv", encoding="utf-8", float_precision="high")
        self.df_tb_test_result = pd.read_csv(path + "df_teacher_behavior_test_result.csv", encoding="utf-8", float_precision="high")

    def tearDown(self):
        pass

    def test_data_pre_processing(self):

        self.tb_obj.data_pre_processing().round(5).to_csv("./tests/examples_FAM/df_tb_data/tb_data_pre_proc_res.csv", index=False)

        processed_data = self.tb_obj.data_pre_processing()
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

    def test_count_lesson_types(self):
        processed_data = self.tb_obj.count_lesson_types(self.tb_obj.data_pre_processing())
        processed_data = processed_data.round(5)
        processed_data = processed_data.to_json()
        res_data = self.count_lesson_types_res.to_json()
        self.assertEquals(
            processed_data,
            res_data
        )

    def test_ask_for_leave_advanced_minutes(self):
        processed_data = self.tb_obj.ask_for_leave_advanced_minutes(self.tb_obj.data_pre_processing())
        processed_data = processed_data.round(5)
        processed_data = processed_data.to_json()
        res_data = self.AFLAM_res
        res_data = res_data.to_json()
        self.assertEquals(
            processed_data,
            res_data
        )

    def test_data_post_processing(self):
        df_count_lesson_types = self.tb_obj.count_lesson_types(self.tb_obj.data_pre_processing())
        df_AFLAM = self.tb_obj.ask_for_leave_advanced_minutes(self.tb_obj.data_pre_processing())
        # 这个函数返回了两个值，其中第一个值等于第一个test的值（根据roger的源码结构）
        processed_data, tmp_data = self.tb_obj.data_post_processing(df_count_lesson_types, df_AFLAM)
        processed_data = processed_data.round(5)
        processed_data = processed_data.astype(str)
        processed_data = processed_data.to_json()
        res_data = self.df_tb_test_result
        res_data = res_data.astype(str)
        res_data = res_data.to_json()
        self.assertEquals(
            processed_data,
            res_data
        )
