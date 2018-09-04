# -*- coding: utf-8 -*-
import unittest
import pandas as pd
import warnings
import datetime
from azj_rating.FA_Model.FAModelMain import FAModelMain
from azj_rating.FA_Model.FAModelDataPreProc import FAModelDataPreProc


class TestFAModelMain(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore")  # 在setup里面初始化指定忽略掉警告
        path = "./tests/examples_FAM/data_main/main_res/"
        origin_path = "./tests/examples_FAM/data_pre_proc/"
        start_time = datetime.datetime(2018, 1, 30, 23, 59, 59)
        end_time = datetime.datetime(2018, 4, 30, 23, 59, 59)
        pre_proc_obj = FAModelDataPreProc(origin_path, start_time, end_time)
        df_wide = pre_proc_obj.gen_df_wide_final()
        self.fa_model_main_obj = FAModelMain(df_wide)
        self.judge_new_teacher_res = pd.read_csv(path + "judge_new_teacher_res.csv")
        self.smooth_0_res = pd.read_csv(path + "smooth_0_res.csv")
        self.smooth_1_res = pd.read_csv(path + "smooth_1_res.csv")
        self.smooth_final_res = pd.read_csv(path + "smooth_final_res.csv")
        self.fix_process_0_res = pd.read_csv(path + "fix_process_0_res.csv")
        self.fix_process_1_res = pd.read_csv(path + "fix_process_1_res.csv")
        self.gen_df_wide_final_res = pd.read_csv(path + "gen_df_wide_final_res.csv")

    def tearDown(self):
        pass

    def test_judge_new_teacher_res(self):
        processed_data = self.fa_model_main_obj.judge_new_teacher().round(5).astype(str).to_json()
        res_data = self.judge_new_teacher_res.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_smooth_process0(self):
        processed_data = self.fa_model_main_obj.smooth_process0().round(5).astype(str).to_json()
        res_data = self.smooth_0_res.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_smooth_process1(self):
        processed_data = self.fa_model_main_obj.smooth_process1().round(5).astype(str).to_json()
        res_data = self.smooth_1_res.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_smooth_process_final(self):
        processed_data = self.fa_model_main_obj.smooth_process_final().round(5).astype(str).to_json()
        res_data = self.smooth_final_res.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_fix_process0(self):
        processed_data = self.fa_model_main_obj.fix_process_0().round(5).astype(str).to_json()
        res_data = self.fix_process_0_res.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_fix_process1(self):
        processed_data = self.fa_model_main_obj.fix_process_1().round(5).astype(str).to_json()
        res_data = self.fix_process_1_res.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_fix_process_final(self):
        processed_data = self.fa_model_main_obj.fix_process_final()[1]
        processed_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.round(5).astype(str).to_json()
        res_data = self.gen_df_wide_final_res
        res_data.reset_index(drop=True, inplace=True)
        res_data = res_data.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )
