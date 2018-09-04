# -*- coding: utf-8 -*-
import unittest
import json
from azj_rating.AwjTeacherStarSnapshot import AwjTeacherStarSnapshot


class TestAwjTeacherStarSnapshot(unittest.TestCase):
    """
    Test for teacher_star_snapshot
    """
    def setUp(self):
        data_path = "./tests/examples/"

        with open(data_path + "with_total_score_data.json") as file:
            total_avg_score = json.load(file)["data"]

        with open(data_path + "star_rate.json") as file:
            star_rate = json.load(file)

        min_qc_score = 5

        coefficient = 0.005

        self.avg_m_ts_snapshot = AwjTeacherStarSnapshot(
            total_avg_score,
            star_rate,
            min_qc_score,
            coefficient
        )

        self.avg_m_origin_data = [
              {'awj_teacher_id': 69,
               'behavior_score': 0.163,
               'qc_score': 0.02166,
               'star_rate': 5,
               'total_score': 0.18466},
              {'awj_teacher_id': 1407,
               'behavior_score': 0.0,
               'qc_score': 0.02044,
               'star_rate': 3,
               'total_score': 0.02044},
              {'awj_teacher_id': 1550,
               'behavior_score': 0.029,
               'qc_score': 0.02055,
               'star_rate': 3,
               'total_score': 0.04955},
              {'awj_teacher_id': 1481,
               'behavior_score': 0.535,
               'qc_score': 0.01956,
               'star_rate': 5,
               'total_score': 0.55456},
              {'awj_teacher_id': 1135,
               'behavior_score': 0.09,
               'qc_score': 0.01934,
               'star_rate': 4,
               'total_score': 0.10934},
              {'awj_teacher_id': 508,
               'behavior_score': 0.211,
               'qc_score': 0.01989,
               'star_rate': 5,
               'total_score': 0.23089},
              {'awj_teacher_id': 885,
               'behavior_score': 0.03375,
               'qc_score': 0.01756,
               'star_rate': 3,
               'total_score': 0.05131},
              {'awj_teacher_id': 1567,
               'behavior_score': 0.0,
               'qc_score': 0.01923,
               'star_rate': 2,
               'total_score': 0.01923},
              {'awj_teacher_id': 718,
               'behavior_score': 0.055,
               'qc_score': 0.02022,
               'star_rate': 4,
               'total_score': 0.07522},
              {'awj_teacher_id': 655,
               'behavior_score': 0.0,
               'qc_score': 0.01978,
               'star_rate': 2,
               'total_score': 0.01978},
              {'awj_teacher_id': 544,
               'behavior_score': 0.098,
               'qc_score': 0.02055,
               'star_rate': 4,
               'total_score': 0.11855},
              {'awj_teacher_id': 1035,
               'behavior_score': 0.15,
               'qc_score': 0.01967,
               'star_rate': 5,
               'total_score': 0.16967},
              {'awj_teacher_id': 1293,
               'behavior_score': 0.13,
               'qc_score': 0.01978,
               'star_rate': 4,
               'total_score': 0.14978},
              {'awj_teacher_id': 1130,
               'behavior_score': 0.171,
               'qc_score': 0.02088,
               'star_rate': 5,
               'total_score': 0.19188},
              {'awj_teacher_id': 1097,
               'behavior_score': 0.0482143,
               'qc_score': 0.01879,
               'star_rate': 3,
               'total_score': 0.0670043},
              {'awj_teacher_id': 1400,
               'behavior_score': 0.01,
               'qc_score': 0.01912,
               'star_rate': 3,
               'total_score': 0.02912},
              {'awj_teacher_id': 1083,
               'behavior_score': 0.08,
               'qc_score': 0.01857,
               'star_rate': 4,
               'total_score': 0.09857},
              {'awj_teacher_id': 1322,
               'behavior_score': 0.025,
               'qc_score': 0.01989,
               'star_rate': 3,
               'total_score': 0.04489},
              {'awj_teacher_id': 1518,
               'behavior_score': 0.0,
               'qc_score': 0.01945,
               'star_rate': 2,
               'total_score': 0.01945},
              {'awj_teacher_id': 890,
               'behavior_score': 0.01,
               'qc_score': 0.01956,
               'star_rate': 3,
               'total_score': 0.02956},
              {'awj_teacher_id': 1008,
               'behavior_score': 0.025,
               'qc_score': 0.01978,
               'star_rate': 3,
               'total_score': 0.04478},
              {'awj_teacher_id': 1277,
               'behavior_score': 0.135,
               'qc_score': 0.02,
               'star_rate': 5,
               'total_score': 0.155},
              {'awj_teacher_id': 355,
               'behavior_score': 0.315,
               'qc_score': 0.02033,
               'star_rate': 5,
               'total_score': 0.33533},
              {'awj_teacher_id': 484,
               'behavior_score': 0.421,
               'qc_score': 0.01923,
               'star_rate': 5,
               'total_score': 0.44023},
              {'awj_teacher_id': 1287,
               'behavior_score': 0.353,
               'qc_score': 0.02022,
               'star_rate': 5,
               'total_score': 0.37322},
              {'awj_teacher_id': 624,
               'behavior_score': 0.0,
               'qc_score': 0.02133,
               'star_rate': 3,
               'total_score': 0.02133},
              {'awj_teacher_id': 429,
               'behavior_score': 0.142,
               'qc_score': 0.02056,
               'star_rate': 5,
               'total_score': 0.16256},
              {'awj_teacher_id': 799,
               'behavior_score': 0.611,
               'qc_score': 0.02044,
               'star_rate': 5,
               'total_score': 0.63144},
              {'awj_teacher_id': 411,
               'behavior_score': 0.063,
               'qc_score': 0.01989,
               'star_rate': 4,
               'total_score': 0.08289},
              {'awj_teacher_id': 752,
               'behavior_score': 0.135,
               'qc_score': 0.02055,
               'star_rate': 5,
               'total_score': 0.15555},
              {'awj_teacher_id': 1490,
               'behavior_score': 0.103,
               'qc_score': 0.01901,
               'star_rate': 4,
               'total_score': 0.12201},
              {'awj_teacher_id': 390,
               'behavior_score': 0.211,
               'qc_score': 0.02011,
               'star_rate': 5,
               'total_score': 0.23111},
              {'awj_teacher_id': 1291,
               'behavior_score': 0.11,
               'qc_score': 0.01879,
               'star_rate': 4,
               'total_score': 0.12879},
              {'awj_teacher_id': 318,
               'behavior_score': 0.078,
               'qc_score': 0.01967,
               'star_rate': 4,
               'total_score': 0.09767},
              {'awj_teacher_id': 1297,
               'behavior_score': 0.135,
               'qc_score': 0.01989,
               'star_rate': 5,
               'total_score': 0.15489},
              {'awj_teacher_id': 97,
               'behavior_score': 0.283,
               'qc_score': 0.01912,
               'star_rate': 5,
               'total_score': 0.30212},
              {'awj_teacher_id': 220,
               'behavior_score': 0.211,
               'qc_score': 0.02033,
               'star_rate': 5,
               'total_score': 0.23133},
              {'awj_teacher_id': 74,
               'behavior_score': 0.133,
               'qc_score': 0.01989,
               'star_rate': 5,
               'total_score': 0.15289},
              {'awj_teacher_id': 592,
               'behavior_score': 0.112342,
               'qc_score': 0.01901,
               'star_rate': 4,
               'total_score': 0.131352},
              {'awj_teacher_id': 835,
               'behavior_score': 0.015,
               'qc_score': 0.01945,
               'star_rate': 3,
               'total_score': 0.03445},
              {'awj_teacher_id': 1219,
               'behavior_score': 0.0971212,
               'qc_score': 0.0189,
               'star_rate': 4,
               'total_score': 0.116021}
        ]

        self.avg_m_sorted_total_score = [
            0.63144, 0.55456, 0.44023, 0.37322, 0.33533, 0.30212, 0.23133, 0.23111,
            0.23089, 0.19188, 0.18466, 0.16967, 0.16256, 0.15555, 0.155, 0.15489, 0.15289,
            0.14978, 0.131352, 0.12879, 0.12201, 0.11855, 0.116021, 0.10934, 0.09857, 0.09767,
            0.08289, 0.07522, 0.0670043, 0.05131, 0.04955, 0.04489, 0.04478, 0.03445, 0.02956,
            0.02912, 0.02133, 0.02044, 0.01978, 0.01945, 0.01923
        ]

        self.avg_m_cal_star_rate_list = [
            0.23111, 0.12879, 0.04489, 0.02912, 0.01923
        ]

        self.avg_m_result_json = [
            {'awj_teacher_id': 69, 'star_rate': 4}, {'awj_teacher_id': 1407, 'star_rate': 1},
            {'awj_teacher_id': 1550, 'star_rate': 3}, {'awj_teacher_id': 1481, 'star_rate': 5},
            {'awj_teacher_id': 1135, 'star_rate': 3}, {'awj_teacher_id': 508, 'star_rate': 4},
            {'awj_teacher_id': 885, 'star_rate': 3}, {'awj_teacher_id': 1567, 'star_rate': 1},
            {'awj_teacher_id': 718, 'star_rate': 3}, {'awj_teacher_id': 655, 'star_rate': 1},
            {'awj_teacher_id': 544, 'star_rate': 3}, {'awj_teacher_id': 1035, 'star_rate': 4},
            {'awj_teacher_id': 1293, 'star_rate': 4}, {'awj_teacher_id': 1130, 'star_rate': 4},
            {'awj_teacher_id': 1097, 'star_rate': 3}, {'awj_teacher_id': 1400, 'star_rate': 2},
            {'awj_teacher_id': 1083, 'star_rate': 3}, {'awj_teacher_id': 1322, 'star_rate': 3},
            {'awj_teacher_id': 1518, 'star_rate': 1}, {'awj_teacher_id': 890, 'star_rate': 2},
            {'awj_teacher_id': 1008, 'star_rate': 2}, {'awj_teacher_id': 1277, 'star_rate': 4},
            {'awj_teacher_id': 355, 'star_rate': 5}, {'awj_teacher_id': 484, 'star_rate': 5},
            {'awj_teacher_id': 1287, 'star_rate': 5}, {'awj_teacher_id': 624, 'star_rate': 1},
            {'awj_teacher_id': 429, 'star_rate': 4}, {'awj_teacher_id': 799, 'star_rate': 5},
            {'awj_teacher_id': 411, 'star_rate': 3}, {'awj_teacher_id': 752, 'star_rate': 4},
            {'awj_teacher_id': 1490, 'star_rate': 3}, {'awj_teacher_id': 390, 'star_rate': 5},
            {'awj_teacher_id': 1291, 'star_rate': 4}, {'awj_teacher_id': 318, 'star_rate': 3},
            {'awj_teacher_id': 1297, 'star_rate': 4}, {'awj_teacher_id': 97, 'star_rate': 5},
            {'awj_teacher_id': 220, 'star_rate': 5}, {'awj_teacher_id': 74, 'star_rate': 4},
            {'awj_teacher_id': 592, 'star_rate': 4}, {'awj_teacher_id': 835, 'star_rate': 2},
            {'awj_teacher_id': 1219, 'star_rate': 3}
        ]

    def tearDown(self):
        pass

    def test_get_total_score_list(self):
        self.assertListEqual(
            self.avg_m_ts_snapshot.get_total_score_list(),
            self.avg_m_sorted_total_score
        )

    def test_cal_star_rate_min_score(self):
        self.assertListEqual(
            self.avg_m_ts_snapshot.cal_star_rate_min_score(
                self.avg_m_sorted_total_score
            ),
            self.avg_m_cal_star_rate_list
        )

    def test_corresponding_star_rate(self):
        self.assertEqual(
            self.avg_m_ts_snapshot.corresponding_star_rate(
                self.avg_m_sorted_total_score[0],
                self.avg_m_cal_star_rate_list
            ),
            5
        )

    def test_total_teacher_star(self):
        self.assertListEqual(
            self.avg_m_ts_snapshot.total_teacher_star(
                self.avg_m_cal_star_rate_list
            ),
            self.avg_m_result_json
        )
