# -*- coding: utf-8 -*-
"""
Configurations for the FA_Model
"""
import pandas
import datetime
import pandas.tseries.offsets


class ConfigurationsFAM(object):

    def __init__(self):
        pass

    @staticmethod
    def get_end_timeslot():
        time_now = pandas.to_datetime(datetime.datetime.now().date())
        month_end_var = pandas.tseries.offsets.MonthEnd(n=-1)
        data_offset = pandas.tseries.offsets.DateOffset(hours=23.99999)
        end_time = time_now + month_end_var + data_offset

        return end_time

    def get_start_timeslot(self):

        start_time = self.get_end_timeslot() - pandas.tseries.offsets.DateOffset(months=3)

        return start_time

    # 因子载荷矩阵作为参数放在设置中，在部署的时候减少读取文件存储文件的麻烦
    @staticmethod
    def get_fa_indexs():
        fa_indexs_dict = {
            'fa_index1': {
                0: -0.062062751606678554,
                1: -0.0870878257539111, 2: -0.027714249554916855, 3: -0.03699536165035535, 4: -0.0322621678605618,
                5: 0.2949437515819686, 6: 0.3248826429205108, 7: 0.3217210622373112, 8: 0.2754657578052482,
                9: 0.023128989626462884
            },
            'fa_index2': {
                0: -0.028543450122578945, 1: -0.01777077217214423, 2: 0.3442964391787648, 3: 0.34602368728379657,
                4: 0.3588747601476948, 5: -0.023287080134318846, 6: -0.028595653057985736, 7: -0.01789428329260495,
                8: -0.0435662419103717, 9: -0.02892002002247041
            },
            'fa_index3': {
                0: 0.530873415803162, 1: 0.545700657054132, 2: -0.03215622252239149, 3: -0.0017256298424077837,
                4: -0.021149364277017118, 5: -0.051459247657691214, 6: -0.07112664527684215, 7: -0.08745009970177652,
                8: -0.01590211180738975, 9: -0.006685857350724741
            },
            'fa_index4': {
                0: 0.00897774984820785, 1: -0.019414166285429885, 2: 0.02811339777122604, 3: -0.060827595099710155,
                4: -0.026614297174764864, 5: -0.005214785935049704, 6: 0.020753826990768935, 7: 0.007255593794369561,
                8: 0.03485688454866179, 9: 1.0002744516704951
            }
        }
        fa_indexs = pandas.DataFrame(fa_indexs_dict)

        return fa_indexs
