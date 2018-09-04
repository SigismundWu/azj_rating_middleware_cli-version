# -*- coding: utf-8 -*-
import unittest
from unittest import mock
import pandas
import pandas.tseries.offsets
import azj_rating.FA_Model.ConfigurationsFAM


class TestConfigurationsFAM(unittest.TestCase):
    def setUp(self):
        self.fa_indexs_res = pandas.read_excel("./tests/examples_FAM/data_pre_proc/fa_indexs.xlsx")

    def tearDown(self):
        pass

    @mock.patch("pandas.to_datetime", autospec=True)
    @mock.patch("pandas.tseries.offsets.MonthEnd", autospec=True)
    @mock.patch("pandas.tseries.offsets.DateOffset", autospec=True)
    def test_get_end_timeslot(self, mock_dateoffset, mock_monthend, mock_datetime):
        pandas.to_datetime(1)
        mock_datetime.return_value = 1
        mock_datetime.assert_called_with(1)
        pandas.tseries.offsets.MonthEnd(2)
        mock_monthend.return_value = 2
        mock_monthend.assert_called_with(2)
        pandas.tseries.offsets.DateOffset(3)
        mock_dateoffset.return_value = 3
        mock_dateoffset.assert_called_with(3)
        config_obj = azj_rating.FA_Model.ConfigurationsFAM.ConfigurationsFAM()
        self.assertEqual(config_obj.get_end_timeslot(), 6)

    @mock.patch("pandas.tseries.offsets.DateOffset", autospec=True)
    @mock.patch("azj_rating.FA_Model.ConfigurationsFAM.ConfigurationsFAM.get_end_timeslot")
    def test_get_star_timeslot(self, mock_gst, mock_dateoffset):
        pandas.tseries.offsets.DateOffset(1)
        mock_dateoffset.return_value = 1
        mock_dateoffset.assert_called_with(1)
        azj_rating.FA_Model.ConfigurationsFAM.ConfigurationsFAM.get_end_timeslot()
        mock_gst.return_value = 2
        mock_gst.assert_called_with()
        config_obj = azj_rating.FA_Model.ConfigurationsFAM.ConfigurationsFAM()
        self.assertEqual(config_obj.get_start_timeslot(), 1)

    def test_get_fa_indexs(self):
        config_obj = azj_rating.FA_Model.ConfigurationsFAM.ConfigurationsFAM()
        fa_indexs = config_obj.get_fa_indexs()
        fa_indexs_d = fa_indexs.to_dict()
        fa_indexs_res_d = self.fa_indexs_res.to_dict()
        self.assertDictEqual(fa_indexs_d, fa_indexs_res_d)
