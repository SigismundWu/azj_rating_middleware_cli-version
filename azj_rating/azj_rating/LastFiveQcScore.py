# -*- coding: utf-8 -*-


class LastFiveQcScore(object):
    """
    This is the class for calculating the avg_score of teachers' QC score
    """
    def __init__(self, original_data, min_qc_scores, coefficient):
        self.need_pack = original_data
        self.min_qc_scores = min_qc_scores
        self.coefficient = coefficient
        self.default_qc_score = 3.75

    def packed_list(self):
        packed = list()
        each_pack = list()

        # 列表解析存在特性上的问题，不适合这个任务，只能用传统方式
        # 找出所有unique的值（无法通过直接遍历找出）
        for index in range(len(self.need_pack) - 1, -1, -1):
            if self.need_pack[index]["awj_teacher_id"] not in each_pack:
                each_pack.append(self.need_pack[index]["awj_teacher_id"])

        for t_id in each_pack:
            tmp_pack = dict()
            tmp_pack["awj_teacher_id"] = t_id
            tmp_pack["qc_score"] = list()
            packed.append(tmp_pack)

        # 找出所有unique的值之后，按照每个unique的值的array，从原列表中pick对应的分数
        final_pack = list()
        for each_teacher_data in packed:
            for index0 in range(len(self.need_pack) - 1, -1, -1):
                if (
                        (self.need_pack[index0]["awj_teacher_id"] == each_teacher_data["awj_teacher_id"])
                        &
                        (len(each_teacher_data["qc_score"]) < self.min_qc_scores)
                        ):
                    if self.need_pack[index0]["qc_score"] is not None:
                        each_teacher_data["qc_score"].append(self.need_pack[index0]["qc_score"])

            final_pack.append(each_teacher_data)

        return final_pack

    def cal_last_five_qc_avg_score(self, final_pack):
        # 业务制定的系数，分数都要乘这个系数
        # 如果不够五次的默认QC分数
        avg_score_final = []
        for data in final_pack:
            if len(data["qc_score"]) < self.min_qc_scores:
                data["qc_score"] = self.default_qc_score * self.coefficient
                avg_score_final.append(data)
            else:
                data["qc_score"] = (
                    (
                            sum(data["qc_score"]) /
                            len(list(data["qc_score"])
                                ) * self.coefficient
                            )
                        )
            avg_score_final.append(data)

        return avg_score_final

    # 计算behavior_score和qc_score总和的total_score并返回
    def cal_total_score(self, avg_score_final):
        for each_teacher_data in avg_score_final:
            for each_pack in self.need_pack:
                if each_teacher_data["awj_teacher_id"] == each_pack["awj_teacher_id"]:
                    each_teacher_data["behavior_score"] = each_pack["behavior_score"]

        for each_set in avg_score_final:
            if each_set["behavior_score"] is not None:
                each_set["total_score"] = each_set["qc_score"] + each_set["behavior_score"]
            else:
                each_set["total_score"] = None

        return avg_score_final


def call_control_funcs(origin_data, min_qc_scores, coefficient):
    data_instance = LastFiveQcScore(origin_data, min_qc_scores, coefficient)
    data_origin = data_instance.packed_list()
    data_tmp = data_instance.cal_last_five_qc_avg_score(data_origin)
    processed_data = data_instance.cal_total_score(data_tmp)

    return processed_data
