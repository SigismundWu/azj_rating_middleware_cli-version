# -*- coding: utf-8 -*-


class PublicMethodsFAM(object):

    def __init__(self):
        pass

    @staticmethod
    def gen_decay_index(end_time, start_time_col):

        day_to_seconds = 3600 * 24

        decay_col = ((end_time - start_time_col).dt.total_seconds()) / day_to_seconds

        return decay_col
