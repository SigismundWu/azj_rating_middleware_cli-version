# -*- coding: utf-8 -*-
import unittest
import warnings
import datetime
import pandas as pd
from azj_rating.FA_Model.FAModelDataPreProc import FAModelDataPreProc


class TestFAModelDataPreProc(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore")  # 在setup里面初始化指定忽略掉警告
        origin_path = "./tests/examples_FAM/data_pre_proc/"
        path = "./tests/examples_FAM/data_pre_proc/pre_proc_res/"
        start_time = datetime.datetime(2018, 1, 30, 23, 59, 59)
        end_time = datetime.datetime(2018, 4, 30, 23, 59, 59)

        self.data_processing_obj = FAModelDataPreProc(origin_path, start_time, end_time)
        self.teacher_monitoring_res = pd.read_csv(path + "教师监控_res.csv", encoding="utf-8")
        self.qc_res = pd.read_csv(path + "教师qc_res.csv", encoding="utf-8")
        self.teacher_behavior_res = pd.read_csv(path + "教师行为_res.csv", encoding="utf-8")
        self.teacher_info_res = pd.read_csv(path + "教师信息_res.csv", encoding="utf-8")
        self.stu_comment_res = pd.read_csv(path + "学生评价_res.csv", encoding="utf-8")
        self.p_qc_res = pd.read_csv(path + "df_qc_res.csv", encoding="utf-8")
        self.p_teacher_behavior_res = pd.read_csv(path + "df_teacher_behavior_res.csv", encoding="utf-8")
        self.p_teacher_behavior_cache_res = pd.read_csv(path + "df_teacher_behavior_cache_res.csv", encoding="utf-8")
        self.p_stu_comment = pd.read_csv(path + "df_stu_comment_res.csv", encoding="utf-8")
        self.df_wide_res = pd.read_csv(path + "df_wide_res.csv", encoding="utf-8")
        self.df_wide_final_res = pd.read_csv(path + "df_wide_final_res.csv", encoding="utf-8")

    def tearDown(self):
        pass

    # 大量数据格式类型的问题
    def test_get_df_teacher_monitoring(self):
        processed_data = self.data_processing_obj.get_df_teacher_monitoring().astype(str).to_json()
        res_data = self.teacher_monitoring_res.astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_get_df_qc(self):
        processed_data = self.data_processing_obj.get_df_qc().astype(str)
        res_data = self.qc_res.astype(str)
        processed_data.reset_index(drop=True, inplace=True)
        res_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.to_json()
        res_data = res_data.to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_get_df_teacher_behavior(self):
        processed_data = self.data_processing_obj.get_df_teacher_behavior().astype(str)
        processed_data = processed_data.replace("NaT", "nan")  # 存在时间序列数据的空值为NaT的问题，在测试中替换，模型中不存在问题
        res_data = self.teacher_behavior_res.astype(str)
        processed_data.reset_index(drop=True, inplace=True)
        res_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.to_json()
        res_data = res_data.to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_get_df_teacher_info(self):
        processed_data = self.data_processing_obj.get_df_teacher_info().astype(str)
        processed_data = processed_data.replace("NaT", "nan")
        processed_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.to_json()
        res_data = self.teacher_info_res.astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_get_df_stu_comment(self):
        processed_data = self.data_processing_obj.get_df_stu_comment().astype(str)
        processed_data = processed_data.replace("NaT", "nan")
        processed_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.to_json()
        res_data = self.stu_comment_res.astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_process_df_qc(self):
        # 需要保留
        df_qc = self.data_processing_obj.get_df_qc()
        processed_data = self.data_processing_obj.process_df_qc(df_qc).round(5).to_json()
        res_data = self.p_qc_res.round(5).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_process_df_teacher_behavior(self):
        df_teacher_behavior = self.data_processing_obj.get_df_teacher_behavior()
        processed_data = self.data_processing_obj.process_df_teacher_behavior(df_teacher_behavior).round(5).to_json()
        res_data = self.p_teacher_behavior_res.round(5).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_process_df_teacher_behavior_cache(self):
        df_teacher_behavior = self.data_processing_obj.get_df_teacher_behavior()
        processed_data = self.data_processing_obj.process_df_teacher_behavior_cache(df_teacher_behavior).astype(str)
        processed_data = processed_data.replace("NaT", "nan")
        processed_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.to_json()
        res_data = self.p_teacher_behavior_cache_res.astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_process_df_stu_comment(self):
        df_teacher_behavior = self.data_processing_obj.get_df_teacher_behavior()
        df_teacher_behavior_cache = self.data_processing_obj.process_df_teacher_behavior_cache(df_teacher_behavior)
        stu_comment = self.data_processing_obj.get_df_stu_comment()
        processed_data = self.data_processing_obj.process_df_stu_comment(stu_comment,
                                                                         df_teacher_behavior_cache).round(5).to_json()
        res_data = self.p_stu_comment.round(5).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_gen_df_wide_prototype(self):
        processed_data = self.data_processing_obj.gen_df_wide_prototype().round(5).astype(str)
        processed_data = processed_data.replace("NaT", "nan")
        processed_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.to_json()
        res_data = self.df_wide_res.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_gen_df_wide_final(self):
        processed_data = self.data_processing_obj.gen_df_wide_final().round(5).astype(str)
        processed_data = processed_data.replace("NaT", "nan")
        processed_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.to_json()
        res_data = self.df_wide_final_res.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )
