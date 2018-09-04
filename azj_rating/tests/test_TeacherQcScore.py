# -*- coding: utf-8 -*-
import unittest
import pandas as pd
import warnings
import datetime
from azj_rating.FA_Model.TeacherQcScore import TeacherQcScore
from azj_rating.FA_Model.FAModelDataPreProc import FAModelDataPreProc


class TestTeacherQcScore(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore")  # 在setup里面初始化指定忽略掉警告
        path = "./tests/examples_FAM/df_qc_data/"
        end_time = datetime.datetime(2018, 4, 30, 23, 59, 59)
        start_time = datetime.datetime(2018, 1, 30, 23, 59, 59)
        class_type_name_special = ['Demo', '补课(非爱乐奇直属老师)', '托福班（30刀）', 'TOFEL',
                                   'VIP Writing/TOFEL（35刀）', 'Elite Pilot', 'Feeback Session',
                                   'New Teacher Test Class', '补课(爱乐奇直属老师)', 'Test Class',
                                   'Academic Meeting (Long)', 'Cur Experience Session-S',
                                   'Training-receiving', 'Cur Experience Session-L',
                                   'VIP Writing/TOFEL', 'Orientation Class', 'Academic Meeting',
                                   'Experience-receiving']
        hq_name_special = ['test']
        # 老师QC明细表
        origin_path = "./tests/examples_FAM/data_pre_proc/"
        data_pre_proc_obj = FAModelDataPreProc(origin_path, start_time, end_time)
        df_qc = data_pre_proc_obj.get_df_qc()
        self.tqs_obj = TeacherQcScore(df_qc, class_type_name_special, hq_name_special, start_time, end_time)
        self.data_pre_processing_res = pd.read_csv(path + "tqs_data_pre_processing_res.csv", encoding="utf-8", float_precision="high")
        self.cal_log_score_mean_res = pd.read_csv(path + "tqs_cal_log_score_mean_res.csv", encoding="utf-8", float_precision="high")
        self.cal_std_missing_res = pd.read_csv(path + "tqs_cal_std_missing_res.csv", encoding="utf-8", float_precision="high")
        self.df_qc_test_result = pd.read_csv(path + "df_qc_test_result.csv", encoding="utf-8", float_precision="high")
        self.df_qc = self.tqs_obj.data_pre_processing()

    def tearDown(self):
        pass

    def test_data_pre_processing(self):
        processed_data = self.tqs_obj.data_pre_processing()
        processed_data.reset_index(drop=True, inplace=True)
        # 强制round，与测试数据保持小数点数量一致
        processed_data = processed_data.round(5)
        processed_data = processed_data.astype(str)
        processed_data = processed_data.to_json()
        # 测试对象被读进来的小数是16位的，而在函数里面产生的小数是17位
        # json格式最多15位，dict同理，因此读取进来之后会有小数位数不同的问题引发的错误，强制round
        res_data = self.data_pre_processing_res.round(5)
        res_data = res_data.astype(str)
        res_data = res_data.to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_cal_log_score_mean(self):
        processed_data = self.tqs_obj.cal_log_score_mean(self.tqs_obj.data_pre_processing())
        processed_data = processed_data.round(5)
        processed_data = processed_data.to_json()
        res_data = self.cal_log_score_mean_res.to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_cal_std_missing(self):
        processed_data = self.tqs_obj.cal_std_missing(self.df_qc)
        processed_data = processed_data.round(5)
        processed_data = processed_data.to_json()
        res_data = self.cal_std_missing_res
        res_data = res_data.to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_data_post_processing(self):
        processed_data = self.tqs_obj.data_post_processing(self.tqs_obj.data_pre_processing())
        processed_data = processed_data.round(5)
        processed_data = processed_data.astype(str)
        processed_data = processed_data.to_json()
        res_data = self.df_qc_test_result
        res_data = res_data.astype(str)
        res_data = res_data.to_json()
        self.assertEqual(
            processed_data,
            res_data
        )
