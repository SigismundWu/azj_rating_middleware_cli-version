# -*- coding: utf-8 -*-
import unittest
import pandas as pd
import warnings
import json
import datetime
from azj_rating.FA_Model.FAModelDataPreProc import FAModelDataPreProc
from azj_rating.FA_Model.FAModelMain import FAModelMain
from azj_rating.FA_Model.GenTeacherStar import GenTeacherStar


class TestGenTeacherStar(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore")  # 在setup里面初始化指定忽略掉警告
        path = "./tests/examples_FAM/data_gen_ts/gen_ts_res/"
        origin_path = "./tests/examples_FAM/data_pre_proc/"
        with open(origin_path + "star_rate.json") as file:
            star_rate = json.load(file)
        fa_indexs = pd.read_excel(origin_path + 'fa_indexs.xlsx')
        start_time = datetime.datetime(2018, 1, 30, 23, 59, 59)
        end_time = datetime.datetime(2018, 4, 30, 23, 59, 59)
        pre_proc_obj = FAModelDataPreProc(origin_path, start_time, end_time)
        df_wide_proc = pre_proc_obj.gen_df_wide_final()
        fa_model_main_obj = FAModelMain(df_wide_proc)
        df_wide, df_wide_final = fa_model_main_obj.fix_process_final()
        self.GTS_obj = GenTeacherStar(star_rate, fa_indexs, df_wide, df_wide_final)
        self.gen_fa_score_dataframe_res = pd.read_csv(path + "gen_fa_score_dataframe_res.csv", encoding="utf-8")
        self.gen_star_rate_res = pd.read_csv(path + "gen_star_rate_res.csv", encoding="utf-8")
        self.gen_final_table_res = pd.read_csv(path + "gen_final_table_res.csv", encoding="utf-8")

    def tearDown(self):
        pass

    def test_gen_fa_score_dataframe(self):
        processed_data = self.GTS_obj.gen_fa_score_dataframe()
        processed_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.round(5).astype(str).to_json()
        res_data = self.gen_fa_score_dataframe_res.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_gen_star_rate_res(self):
        processed_data = self.GTS_obj.gen_star_rate()
        processed_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.round(5).astype(str).to_json()
        res_data = self.gen_star_rate_res.round(5).astype(str).to_json()
        self.assertEqual(
            processed_data,
            res_data
        )

    def test_gen_final_table(self):
        processed_data = self.GTS_obj.gen_final_table()
        processed_data.reset_index(drop=True, inplace=True)
        processed_data = processed_data.round(5)
        processed_data = processed_data.round(5).astype(str).to_json()
        res_data = self.gen_final_table_res.round(5).astype(str)
        res_data = res_data.replace("nan", "null").to_json()
        self.assertEqual(
            processed_data,
            res_data
        )
