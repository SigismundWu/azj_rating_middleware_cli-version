# -*- coding: utf-8 -*-
import unittest
import json
# mock掉内置函数的时候需要import builtins来替代原有的内置函数
from unittest import mock
import warnings
import pandas as pd
from azj_rating.AutomaticFAM import AutomaticFAM
warnings.simplefilter("ignore")


class TestAutomaticFAM(unittest.TestCase):

    @mock.patch("azj_rating.AutomaticFAM.pymysql.connect", autospec=True)
    def setUp(self, mock_pymysql):
        warnings.simplefilter("ignore")
        test_configs_path = "./tests/configs_for_test/"
        with open("".join([test_configs_path, "conn_info.json"])) as file:
            data_conn = json.load(file)
        with open("".join([test_configs_path, "teacher_star_vars.json"])) as file:
            data_vars = json.load(file)

        self.afam_obj = AutomaticFAM(data_conn, data_vars)
        self.path_sql_for_test = "./tests/examples_FAM/automatic_fam/"
        self.stmt_result = "select * from table_a, select * from table_b;"

    def tearDown(self):
        pass

    def test_get_stmt(self):
        input_data = "".join([self.path_sql_for_test, "data_of_stmt_test.sql"])
        answer = self.afam_obj.get_stmt(input_data)
        self.assertEqual(answer, self.stmt_result)

    # 几个以游标获取数据的函数，写法一致，mock对象一致，在一个测试函数里面完成测试
    @mock.patch("azj_rating.AutomaticFAM.pd.DataFrame.to_csv")
    @mock.patch("azj_rating.AutomaticFAM.pd.read_sql")
    @mock.patch("azj_rating.AutomaticFAM.AutomaticFAM.get_stmt")
    def test_data_value_get(self, mock_stmt, mock_readsql, mock_csv):
        mock_stmt(1)
        mock_stmt.return_value = 2
        # 第二个函数依赖第一个的返回结果作为参数
        mock_readsql(2)
        mock_readsql.assert_called_with(2)
        mock_csv(3)
        self.assertEqual(self.afam_obj.value_teacher_behavior(), 0)
        self.assertEqual(self.afam_obj.value_teacher_info(), 0)
        self.assertEqual(self.afam_obj.value_student_comment(), 0)
        self.assertEqual(self.afam_obj.value_qc_score(), 0)
        self.assertEqual(self.afam_obj.value_teacher_monitoring(), 0)

    # star_rate需要额外mock
    @mock.patch("json.dump")
    # builtin
    @mock.patch("builtins.open")
    @mock.patch("azj_rating.AutomaticFAM.pd.read_sql")
    @mock.patch("azj_rating.AutomaticFAM.AutomaticFAM.get_stmt")
    def test_star_rate_value_get(self, mock_stmt, mock_sql, mock_open, mock_dump):
        mock_stmt(1)
        mock_stmt.return_value = 2
        mock_sql(2)
        # 模拟DataFrame
        mock_sql.return_value = pd.DataFrame(
            [[0.2, 0.5, 0.8, 0.9, 1.0]],
            columns=["five_star_rate", "four_star_rate", "three_star_rate", "two_star_rate", "one_star_rate"]
        )
        mock_dump()
        mock_open()
        self.assertEqual(self.afam_obj.value_star_rate(), 0)

    @mock.patch("azj_rating.AutomaticFAM.AutomaticFAM.value_star_rate")
    @mock.patch("azj_rating.AutomaticFAM.AutomaticFAM.value_qc_score")
    @mock.patch("azj_rating.AutomaticFAM.AutomaticFAM.value_student_comment")
    @mock.patch("azj_rating.AutomaticFAM.AutomaticFAM.value_teacher_info")
    @mock.patch("azj_rating.AutomaticFAM.AutomaticFAM.value_teacher_monitoring")
    @mock.patch("azj_rating.AutomaticFAM.AutomaticFAM.value_teacher_behavior")
    def test_gen_data_sets(self, mock_behavior, mock_monitor, mock_info, mock_comment, mock_qc, mock_star_rate):
        # 几个mock函数互不依赖
        mock_behavior()
        mock_monitor()
        mock_info()
        mock_comment()
        mock_qc()
        mock_star_rate()
        self.assertEqual(self.afam_obj.gen_data_sets(), 0)

    # 只mock最后的输出到csv，其他部分
    @mock.patch("azj_rating.AutomaticFAM.pd.DataFrame.to_csv")
    def test_auto_fa_model(self, mock_csv):
        mock_csv()
        self.assertEqual(self.afam_obj.auto_fa_model(), 0)
