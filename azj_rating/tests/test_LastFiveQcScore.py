# -*- coding: utf-8 -*-
import unittest
import json
from azj_rating import LastFiveQcScore


class TestLastFiveQcScore(unittest.TestCase):
    """
    Test for cal_star_rate
    """
    def setUp(self):

        with open("./tests/examples/origin_teacher_star_data.json") as file:
            self.data = json.load(file)["data"]

        self.min_qc_score = 5
        self.coefficient = 0.005
        self.avg_score = LastFiveQcScore.LastFiveQcScore(self.data, self.min_qc_score, self.coefficient)

        self.score_total = [
            {'awj_teacher_id': 1550, 'qc_score': [2.4, 1.8, 2.1, 4.1, 5.0]},
            {'awj_teacher_id': 1407, 'qc_score': [4.9, 3.6, 2.8, 1.9, 3.9]},
            {'awj_teacher_id': 1931, 'qc_score': []},
            {'awj_teacher_id': 617, 'qc_score': [3.6, 2.5]},
            {'awj_teacher_id': 69, 'qc_score': [2.8, 4.0, 3.1, 2.8, 3.8]}
        ]

        self.avg_final = [
            {'awj_teacher_id': 1550, 'qc_score': 0.0154}, {'awj_teacher_id': 1407, 'qc_score': 0.0171},
            {'awj_teacher_id': 1931, 'qc_score': 0.01875}, {'awj_teacher_id': 1931, 'qc_score': 0.01875},
            {'awj_teacher_id': 617, 'qc_score': 0.01875}, {'awj_teacher_id': 617, 'qc_score': 0.01875},
            {'awj_teacher_id': 69, 'qc_score': 0.0165}
        ]

        self.total_final = [
            {'awj_teacher_id': 1550, 'qc_score': 0.0154, 'behavior_score': 0.029, 'total_score': 0.0444},
            {'awj_teacher_id': 1407, 'qc_score': 0.0171, 'behavior_score': 0.0, 'total_score': 0.0171},
            {'awj_teacher_id': 1931, 'qc_score': 0.01875, 'behavior_score': None, 'total_score': None},
            {'awj_teacher_id': 1931, 'qc_score': 0.01875, 'behavior_score': None, 'total_score': None},
            {'awj_teacher_id': 617, 'qc_score': 0.01875, 'behavior_score': 0.124, 'total_score': 0.14275},
            {'awj_teacher_id': 617, 'qc_score': 0.01875, 'behavior_score': 0.124, 'total_score': 0.14275},
            {'awj_teacher_id': 69, 'qc_score': 0.0165, 'behavior_score': 0.163, 'total_score': 0.1795}
        ]

    def tearDown(self):
        pass

    def test_packed_list(self):
        self.assertListEqual(
            self.avg_score.packed_list(),
            self.score_total
        )

    def test_cal_last_five_qc_avg_score(self):
        self.assertListEqual(
            self.avg_score.cal_last_five_qc_avg_score(
                self.score_total
            ),
            self.avg_final
        )

    def test_cal_total_score(self):
        self.assertListEqual(
            self.avg_score.cal_total_score(self.avg_final),
            self.total_final
        )

    def test_call_control_funcs(self):
        self.assertListEqual(
            LastFiveQcScore.call_control_funcs(self.data, self.min_qc_score, self.coefficient),
            self.total_final
        )
