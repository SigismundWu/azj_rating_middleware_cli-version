# -*- coding: utf-8 -*-
import os
import json
from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

# 执行路径（airflow dag）及配置文件存放路径
exec_path = os.path.dirname(os.path.abspath(__file__))
config_path = "".join([exec_path, "/../", "configs/"])
conn_info_path = "".join([config_path, "conn_info.json"])
teacher_star_vars_path = "".join([config_path, "teacher_star_vars.json"])
s3_base_config_path = "".join([config_path, "airflow_config.json"])
with open(s3_base_config_path) as file:
    s3_base_path = json.load(file)
s3_base_path = s3_base_path["s3_base_path"]
# 实际存放数据，进行数据操作的路径
with open(teacher_star_vars_path) as file:
    vars = json.load(file)
tmp_path = vars[0]  # tmp，第一个参数
FAM_result_path = vars[3]   # result，第四个参数

# 默认dag参数
default_args = {
    'owner': 'bingcong.wu',
    'depends_on_past': False,
    'start_date': datetime(2018, 6, 26),
    'email': ['bingcong.wu@alo7.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(seconds=10),
    # 'end_date': datetime(2018, 6, 30)
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,

}

# 确定dag参数, 每天执行一次
dag = DAG('azj_rating', default_args=default_args, schedule_interval="0 0 * * *")

# 自动获取两个工作的json，然后添加到内容里面
automatic_fam_task = BashOperator(
    task_id='automatic_fam_task',
    bash_command=" ".join(['azj_rating', 'FAM_airflow', conn_info_path, teacher_star_vars_path]),
    dag=dag
)

# 完成后删除使用过的temp数据
clear_tmp_files = BashOperator(
    task_id="clear_tmp_files",
    bash_command="".join(["rm", " ", "-rf", " ", tmp_path, "*"]),
    dag=dag
)

# 添加一个把生成好的文件push到s3的指令, 请补全s3_command
# 逻辑：永远只有一个文件在FAM_result文件夹下，所以整个文件夹push亦可
push_to_s3 = BashOperator(
    task_id="push_to_s3",
    bash_command="/usr/local/bin/aws s3 --profile azj_rating cp --recursive {0}/ {1}/".format(FAM_result_path, s3_base_path),
    dag=dag

)

# rm -rf FAM_result_path/*
clear_deprecated_file = BashOperator(
    task_id="clear_deprecated_file",
    bash_command="".join(["rm", " ", "-rf", " ", FAM_result_path, "*"]),
    dag=dag
)

clear_tmp_files.set_upstream(automatic_fam_task)
push_to_s3.set_upstream(clear_tmp_files)
clear_deprecated_file.set_upstream(push_to_s3)
