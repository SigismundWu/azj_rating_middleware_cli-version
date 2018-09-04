# -*- coding: utf-8 -*-


class AwjTeacherStarSnapshot(object):
    """
    This is the main class for the calculation of the teacher_stars
    """
    def __init__(self, total_score, star_rate, min_qc_score, coefficient):
        self.star_rate = star_rate
        self.min_qc_score = min_qc_score
        self.coefficient = coefficient
        self.total_score = total_score

    def get_total_score_list(self):
        sorted_total_score_list = []

        for each_teacher_info in self.total_score:

            if each_teacher_info["total_score"] is not None:
                sorted_total_score_list.append(each_teacher_info["total_score"])

        sorted_total_score_list.sort(reverse=True)
        return sorted_total_score_list

    def cal_star_rate_min_score(self, sorted_total_score):
        # star_rate数据中等级和对应比例进行提取，生成对应中位数的列表
        cal_star_rate_list = [
            sorted_total_score[int(len(sorted_total_score) * level["rate"]) - 1] for level in self.star_rate
        ]

        return cal_star_rate_list

    @staticmethod
    def corresponding_star_rate(each_score, cal_star_rate_list):
        star_rate = None

        if each_score is None:
            star_rate = 3
        elif each_score >= cal_star_rate_list[0]:
            star_rate = 5
        elif each_score >= cal_star_rate_list[1]:
            star_rate = 4
        elif each_score >= cal_star_rate_list[2]:
            star_rate = 3
        elif each_score >= cal_star_rate_list[3]:
            star_rate = 2
        elif each_score >= cal_star_rate_list[4]:
            star_rate = 1

        return star_rate

    def total_teacher_star(self, cal_star_rate_list):
        final_star_rate_list = []

        for each_teacher_info in self.total_score:
            each_teacher_star_data = dict()
            each_teacher_star_data["awj_teacher_id"] = each_teacher_info["awj_teacher_id"]
            each_teacher_star_data["star_rate"] = self.corresponding_star_rate(
                each_teacher_info["total_score"],
                cal_star_rate_list
            )
            final_star_rate_list.append(each_teacher_star_data)

        return final_star_rate_list
