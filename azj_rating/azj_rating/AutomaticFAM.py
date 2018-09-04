# -*- coding: utf-8 -*-
import re
import json
import time
import pymysql
import pandas as pd
from azj_rating.FA_Model.ConfigurationsFAM import ConfigurationsFAM
from azj_rating.FA_Model.FAModelMain import FAModelMain
from azj_rating.FA_Model.FAModelDataPreProc import FAModelDataPreProc
from azj_rating.FA_Model.GenTeacherStar import GenTeacherStar


class AutomaticFAM(object):
    """
    Automatically get data from DB and gen the FAM
    conn_info : A dict contains host, port, user, passwd, charset and database information
    teacher_star_vars: A list contains the vars for GenTeacherStar, [data_path, star_rate, output]
    storage_path: The same as the data_path of cil_vars
    examples for initiating the AutomaticFAM object:
    """
    def __init__(self, conn_info, teacher_star_vars):
        self.teacher_star_vars = teacher_star_vars
        self.storage_path = self.teacher_star_vars[0]  # The path is a positional argument, at the first place
        self.star_rate = self.teacher_star_vars[1]  # star_rate.json
        self.sql_files = self.teacher_star_vars[2]  # The path storage the sql files
        self.output_path = self.teacher_star_vars[3]  # output path
        self.conn = pymysql.connect(
            host=conn_info["host"], port=conn_info["port"], user=conn_info["user"],
            passwd=conn_info["passwd"], charset=conn_info["charset"], database=conn_info["database"]
        )
        date_time = time.localtime()
        self.date_of_result = "".join(map(str, [date_time.tm_year, "-", date_time.tm_mon, "-", date_time.tm_mday]))

    def get_stmt(self, sql_file):

        with open(sql_file) as file:
            stmt = file.read()
        # 处理Lucas给到的sql语句，去掉换行符，改成单行的长语句
        # 除去注释等，避免麻烦
        stmt = re.sub(r"(?<=-- ).+(\n)", " ", stmt)
        stmt = re.sub(r"--", "", stmt)
        stmt = re.sub(r"\n +", " ", stmt)
        return stmt

    # get data from the sql
    # 老师行为信息明细
    def value_teacher_behavior(self):
        stmt = self.get_stmt(self.sql_files + "老师行为信息明细.sql")

        data = pd.read_sql(stmt, self.conn)
        data.to_csv(self.storage_path + "老师行为信息明细.csv", encoding="utf-8", index=False)

        return 0

    # 老师基本信息
    def value_teacher_info(self):
        stmt = self.get_stmt(self.sql_files + "老师基本信息.sql")

        data = pd.read_sql(stmt, self.conn)
        data.to_csv(self.storage_path + "老师基本信息.csv", encoding="utf-8", index=False)

        return 0

    # 学生评价
    def value_student_comment(self):
        stmt = self.get_stmt(self.sql_files + "学生评价明细.sql")

        data = pd.read_sql(stmt, self.conn)
        data.to_csv(self.storage_path + "学生评价明细.csv", encoding="utf-8", index=False)

        return 0

    # 老师QC明细
    def value_qc_score(self):
        stmt = self.get_stmt(self.sql_files + "QC明细.sql")

        data = pd.read_sql(stmt, self.conn)
        data.to_csv(self.storage_path + "老师qc明细.csv", encoding="utf-8", index=False)

        return 0

    def value_teacher_monitoring(self):
        stmt = self.get_stmt(self.sql_files + "awj_teacher_monitoring.sql")

        data = pd.read_sql(stmt, self.conn)
        data.to_csv(self.storage_path + "awj_teacher_monitoring.csv", encoding="utf-8", index=False)

        return 0

    def value_star_rate(self):
        stmt = self.get_stmt(self.sql_files + "老师星级比例参数配置.sql")

        data = pd.read_sql(stmt, self.conn)
        data = data.T
        data_jc = eval(data.to_json())
        json_list = list()

        for k, v in data_jc["0"].items():
            dict_tmp = dict()
            dict_tmp["stars"] = k
            dict_tmp["rate"] = v
            json_list.append(dict_tmp)

        with open(self.storage_path + "star_rate.json", "w") as file:
            json.dump(json_list, file)

        return 0

    def gen_data_sets(self):
        self.value_teacher_behavior()
        self.value_teacher_monitoring()
        self.value_teacher_info()
        self.value_student_comment()
        self.value_qc_score()
        self.value_star_rate()

        return 0

    def auto_fa_model(self):
        pre_proc_obj = FAModelDataPreProc(self.storage_path)
        df_wide_proc = pre_proc_obj.gen_df_wide_final()
        fa_main_obj = FAModelMain(df_wide_proc)
        df_wide, df_wide_final = fa_main_obj.fix_process_final()
        with open(self.star_rate) as file:
            star_rate = json.load(file)
        config_obj = ConfigurationsFAM()
        fa_indexs = config_obj.get_fa_indexs()
        gen_ts_obj = GenTeacherStar(star_rate, fa_indexs, df_wide, df_wide_final)
        data_processed_with_fam = gen_ts_obj.gen_final_table()

        # 限制五位小数，确保模型精度并且在转化为json的时候避免问题
        data_processed_with_fam.to_csv("".join([self.output_path, self.date_of_result, "_FAM_result.csv"]),
                                       encoding="utf-8", index=False, float_format='%.5f')

        return 0
