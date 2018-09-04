# -*- coding: utf-8 -*-
import unittest
import pandas as pd
from azj_rating.FA_Model.PublicMethodsFAM import PublicMethodsFAM


class TestPublicMethodsFAM(unittest.TestCase):

    def setUp(self):
        self.end_time = pd.to_datetime("1997/10/15 23:20:40")
        self.start_time_col = pd.to_datetime(pd.Series(["1997/10/15 23:20:20", "1997/10/15 23:20:30"]))
        self.gdi_t_result = pd.Series([0.000231, 0.000116])

    def tearDown(self):
        pass

    def test_gen_decay_index(self):
        result = list(PublicMethodsFAM.gen_decay_index(self.end_time, self.start_time_col).round(6))
        answer = list(self.gdi_t_result)
        self.assertListEqual(result, answer)
