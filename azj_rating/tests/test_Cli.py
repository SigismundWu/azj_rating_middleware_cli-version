# -*- coding: utf-8 -*-
import unittest
import sys
import json
from io import StringIO
from unittest import mock
import warnings

from azj_rating import cli
import azj_rating.AutomaticFAM


class TestCli(unittest.TestCase):
    """
        Test for cli (the main)
        Test the main function's return
    """
    def setUp(self):
        warnings.simplefilter("ignore")
        self.test_normal_args = [
            "normal",
            "with_total_score",
            "./tests/examples/with_total_score_data.json",
            "./tests/examples/star_rate.json",
            "--output", "./tests/examples/output.json",
            "--min_qc_scores", "5",
            "--coefficient", "0.005"
        ]

        self.test_fam_args = [
            "FAM",
            "data_path",
            "--output", "output_path"
        ]

        self.test_fam_airflow_args = [
            "FAM_airflow",
            "conn_info",
            "teacher_star_vars"
        ]

    def tearDown(self):
        pass

    def test_create_parser(self):
        args_normal = cli.create_parser(self.test_normal_args)
        self.assertEqual(args_normal.mode, "with_total_score")
        self.assertEqual(args_normal.teacher_star_data, "./tests/examples/with_total_score_data.json")
        self.assertEqual(args_normal.star_rate_data, "./tests/examples/star_rate.json")
        self.assertEqual(args_normal.output, "./tests/examples/output.json")
        self.assertEqual(args_normal.min_qc_scores, 5)
        self.assertEqual(args_normal.coefficient, 0.005)

        args_fam = cli.create_parser(self.test_fam_args)
        self.assertEqual(args_fam.data_path, "data_path")
        self.assertEqual(args_fam.output, "output_path")

        args_fam_airflow = cli.create_parser(self.test_fam_airflow_args)
        self.assertEqual(args_fam_airflow.conn_info, "conn_info")
        self.assertEqual(args_fam_airflow.teacher_star_vars, "teacher_star_vars")

    def test_data_processing(self):

        test_data_origin = {
            "sub_command": "normal",
            "mode": "origin",
            "teacher_star_data": "./tests/examples/origin_teacher_star_data.json",
            "star_rate_data": "./tests/examples/star_rate.json",
            "output": "./tests/examples/output.json",
            "min_qc_scores": 5,
            "coefficient": 0.005
        }

        self.assertEqual(
            cli.data_processing(
                test_data_origin["mode"], test_data_origin["teacher_star_data"], test_data_origin["star_rate_data"],
                test_data_origin["output"], test_data_origin["min_qc_scores"], test_data_origin["coefficient"]
            ),
            0
        )

        test_data_exception = {
            "mode": "wrong_mode",
            "teacher_star_data": "./tests/examples/origin_teacher_star_data.json",
            "star_rate_data": "./tests/examples/star_rate.json",
            "output": "./tests/examples/output.json",
            "min_qc_scores": 5,
            "coefficient": 0.005
        }

        self.assertRaises(
            Exception, lambda: cli.data_processing(
                test_data_exception["mode"], test_data_exception["teacher_star_data"],
                test_data_exception["star_rate_data"], test_data_exception["output"],
                test_data_exception["min_qc_scores"], test_data_exception["coefficient"]
            )
        )

        test_data_wts = {
            "mode": "with_total_score",
            "teacher_star_data": "./tests/examples/with_total_score_data.json",
            "star_rate_data": "./tests/examples/star_rate.json",
            "output": "./tests/examples/output.json",
            "min_qc_scores": 5,
            "coefficient": 0.005
        }

        self.assertEqual(
            cli.data_processing(
                test_data_wts["mode"], test_data_wts["teacher_star_data"],
                test_data_wts["star_rate_data"], test_data_wts["output"],
                test_data_wts["min_qc_scores"], test_data_wts["coefficient"]
            ),
            0
        )

        test_data_stdout = {
            "mode": "with_total_score",
            "teacher_star_data": "./tests/examples/with_total_score_data.json",
            "star_rate_data": "./tests/examples/star_rate.json",
            "min_qc_scores": 5,
            "coefficient": 0.005
        }

        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            cli.data_processing(
                test_data_stdout["mode"], test_data_stdout["teacher_star_data"], test_data_stdout["star_rate_data"],
                sys.stdout, test_data_stdout["min_qc_scores"], test_data_stdout["coefficient"]
            )
            expected_output = [
                {"awj_teacher_id": 69, "star_rate": 4}, {"awj_teacher_id": 1407, "star_rate": 1},
                {"awj_teacher_id": 1550, "star_rate": 3}, {"awj_teacher_id": 1481, "star_rate": 5},
                {"awj_teacher_id": 1135, "star_rate": 3}, {"awj_teacher_id": 508, "star_rate": 4},
                {"awj_teacher_id": 885, "star_rate": 3}, {"awj_teacher_id": 1567, "star_rate": 1},
                {"awj_teacher_id": 718, "star_rate": 3}, {"awj_teacher_id": 655, "star_rate": 1},
                {"awj_teacher_id": 544, "star_rate": 3}, {"awj_teacher_id": 1035, "star_rate": 4},
                {"awj_teacher_id": 1293, "star_rate": 4}, {"awj_teacher_id": 1130, "star_rate": 4},
                {"awj_teacher_id": 1097, "star_rate": 3}, {"awj_teacher_id": 1400, "star_rate": 2},
                {"awj_teacher_id": 1083, "star_rate": 3}, {"awj_teacher_id": 1322, "star_rate": 3},
                {"awj_teacher_id": 1518, "star_rate": 1}, {"awj_teacher_id": 890, "star_rate": 2},
                {"awj_teacher_id": 1008, "star_rate": 2}, {"awj_teacher_id": 1277, "star_rate": 4},
                {"awj_teacher_id": 355, "star_rate": 5}, {"awj_teacher_id": 484, "star_rate": 5},
                {"awj_teacher_id": 1287, "star_rate": 5}, {"awj_teacher_id": 624, "star_rate": 1},
                {"awj_teacher_id": 429, "star_rate": 4}, {"awj_teacher_id": 799, "star_rate": 5},
                {"awj_teacher_id": 411, "star_rate": 3}, {"awj_teacher_id": 752, "star_rate": 4},
                {"awj_teacher_id": 1490, "star_rate": 3}, {"awj_teacher_id": 390, "star_rate": 5},
                {"awj_teacher_id": 1291, "star_rate": 4}, {"awj_teacher_id": 318, "star_rate": 3},
                {"awj_teacher_id": 1297, "star_rate": 4}, {"awj_teacher_id": 97, "star_rate": 5},
                {"awj_teacher_id": 220, "star_rate": 5}, {"awj_teacher_id": 74, "star_rate": 4},
                {"awj_teacher_id": 592, "star_rate": 4}, {"awj_teacher_id": 835, "star_rate": 2},
                {"awj_teacher_id": 1219, "star_rate": 3}
            ]
            self.assertEqual(eval(fake_out.getvalue()), expected_output)

    def test_fa_model(self):
        test_data_fam = {
            "mode": "FA_Model",
            "teacher_star_data_path": "./tests/examples_FAM/data_pre_proc/",
            "output": "./tests/examples_FAM/data_cli_fa/result.csv",
        }

        self.assertEqual(
            cli.use_fa_model(
                test_data_fam["teacher_star_data_path"], test_data_fam["output"],
            ),
            0
        )

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_fa_model_stdout(self, mock_stdout):
        test_data_fam_stdout = {
            "mode": "FA_Model",
            "teacher_star_data_path": "./tests/examples_FAM/data_pre_proc/",
            "output": sys.stdout
        }
        # 必须明确参数sys.stdout，否则在mock的行为中，会先断言再抛出stdout
        cli.use_fa_model(test_data_fam_stdout["teacher_star_data_path"], sys.stdout)
        expected_output = {
            "teacher_behavior_score":{"0":5.0,"1":4.69766,"2":1.88622,"3":1.1618,"4":1.76498,"5":0.19036,"6":0.0,"7":0.36102,"8":0.46553,"9":0.55844,"10":"null"},
            "teacher_qc_score":{"0":5.0,"1":4.52833,"2":2.59668,"3":2.84501,"4":1.83863,"5":1.13667,"6":4.37543,"7":1.44107,"8":1.56596,"9":0.0,"10":"null"},
            "teacher_attitude_score":{"0":3.75099,"1":3.816,"2":4.51465,"3":4.36702,"4":2.76804,"5":5.0,"6":1.86809,"7":2.26786,"8":0.0,"9":0.29242,"10":"null"},
            "student_comment_score":{"0":3.60466,"1":3.47104,"2":2.72151,"3":1.54459,"4":3.19328,"5":5.0,"6":0.03024,"7":1.79218,"8":0.0,"9":0.07996,"10":"null"},
            "final_score":{"0":5.0,"1":4.69475,"2":2.63455,"3":2.12198,"4":2.0761,"5":1.68003,"6":1.23072,"7":0.90802,"8":0.32507,"9":0.0,"10":"null"},
            "awj_teacher_id":{"0":0,"1":1,"2":5,"3":2,"4":3,"5":4,"6":7,"7":6,"8":9,"9":8,"10":10},"star":{"0":5.0,"1":5.0,"2":4.0,"3":4.0,"4":4.0,"5":3.0,"6":3.0,"7":3.0,"8":2.0,"9":1.0,"10":0.0},
            "normal_lesson_log_count":{"0":98.18093,"1":91.94962,"2":48.72695,"3":31.20911,"4":48.32367,"5":4.84792,"6":0.30103,"7":7.27997,"8":0.30103,"9":0.30103,"10":"null"}
        }
        self.assertEqual(eval(mock_stdout.getvalue()), expected_output)

    @mock.patch("azj_rating.AutomaticFAM.AutomaticFAM.gen_data_sets", autospec=True)
    @mock.patch("azj_rating.AutomaticFAM.AutomaticFAM.auto_fa_model", autospec=True)
    @mock.patch("azj_rating.AutomaticFAM.pymysql.connect", autospec=True)
    def test_fam_airflow(self, mock_gen_ds, mock_afm, mock_pymysql):
        test_data_fam_airflow = {
            "mode": "FAM_airflow",
            "conn_info": "./tests/configs_for_test/conn_info.json",
            "teacher_star_vars": "./tests/configs_for_test/teacher_star_vars.json"
        }
        with open(test_data_fam_airflow["conn_info"]) as file:
            data_conn = json.load(file)
        with open(test_data_fam_airflow["teacher_star_vars"]) as file:
            data_tsv = json.load(file)
        auto_fam_obj = azj_rating.AutomaticFAM.AutomaticFAM(data_conn, data_tsv)
        auto_fam_obj.gen_data_sets()
        mock_gen_ds.return_value = 1
        auto_fam_obj.auto_fa_model()
        mock_afm.return_value = 1
        self.assertEqual(cli.auto_fam_with_sql(test_data_fam_airflow["conn_info"], test_data_fam_airflow["teacher_star_vars"]), 0)

    def test_for_main_mock(self):
        cli.create_parser = mock.Mock()
        cli.data_processing = mock.Mock()
        cli.create_parser(self.test_normal_args)
        cli.create_parser.assert_called_with(self.test_normal_args)
        cli.data_processing("mode", "teacher_star_data", "star_rate_data", "output", "min_qc_scores", "coefficient")
        cli.data_processing.assert_called_with(
            "mode", "teacher_star_data", "star_rate_data", "output", "min_qc_scores", "coefficient"
        )

        self.assertEqual(cli.main(self.test_normal_args), 0)

    def test_for_main_fam_mock(self):
        test_data = [
            "FAM",
            "./tests/examples_FAM/data_pre_proc/",
            "--output", "./tests/examples_FAM/data_cli_fa/result.csv",
        ]
        cli.use_fa_model = mock.Mock()
        cli.use_fa_model("teacher_star_data_path", "star_rate_data")
        cli.use_fa_model.assert_called_with(
            "teacher_star_data_path", "star_rate_data"
        )

        self.assertEqual(cli.main(test_data), 0)

    def test_for_main_fam_airflow_mock(self):
        test_data = [
            "FAM_airflow",
            "conn_info.json",
            "teacher_star_vars.json"
        ]
        cli.auto_fam_with_sql = mock.Mock()
        cli.auto_fam_with_sql("conn_info.json", "teacher_star_vars.json")
        cli.auto_fam_with_sql.assert_called_with(
            "conn_info.json", "teacher_star_vars.json"
        )

        self.assertEqual(cli.main(test_data), 0)

    def test_for_main_value_exception(self):
        # 针对只输入一个azj_rating并没有其他参数的情况，实际情况是一个空列表
        wrong_input = []
        self.assertRaises(ValueError, lambda: cli.main(wrong_input))
