#! /bin/bash

set -ex

PROJECT_GIT_DIR=git@git.sxqweqdfgaxyxxxboxxt.nxxaexxt:bingcong.wu/azj_rating-airflow.git
LOCAL_TMP_DIR=/tmp/azj_rating
LOCAL_CONFIG_DIR=/etc/alo7_dw/azj_rating



# 配置环境信息
case $DEPLOY_ENVIRENMENT in
'dev')
  deploy_host="localhost"
  branch="dev"
  remote_project_home="/Users/calvin/airflow_deploy_project"
  remote_airflow_home="/Users/calvin/airflow"
  ;;
'beta')
  deploy_host="airflow@airflow-beta"
  branch="beta"
  remote_project_home="/scheduler/projects"
  remote_airflow_home="/scheduler/airflow"
  ;;
'rc'*)
  deploy_host="ubuntu@airflow-18"
  branch="rc"
  remote_project_home="/scheduler/projects"
  remote_airflow_home="/scheduler/airflow"
  ;;
'18'*)
  deploy_host="ubuntu@airflow-18"
  branch="rc"
  remote_project_home="/scheduler/projects"
  remote_airflow_home="/scheduler/airflow"
  ;;
'production')
  deploy_host="ubuntu@airflow-production"
  branch="master"
  remote_project_home="/scheduler/projects"
  remote_airflow_home="/scheduler/airflow"
  ;;
*)
  Message="NEED CONFIG DEPLOY_ENVIRENMENT"
  exit -1
  ;;
esac


# 需要替换的配置目录
CONFIG_DIRS=(
  "${LOCAL_TMP_DIR}/azj_rating/configs:${LOCAL_CONFIG_DIR}/${DEPLOY_ENVIRENMENT}/"
  )

log "BEGIN: Generate temporary directories"
if [[ "${LOCAL_TMP_DIR##/tmp/}" != "${LOCAL_TMP_DIR}" ]]; then
  # 目录在/tmp 目录下
  rm -r -f $LOCAL_TMP_DIR
else
  exit -2
fi
mkdir -p $LOCAL_TMP_DIR
log "FINISH: Generate temporary directories($LOCAL_TMP_DIR)"


# 下载项目
log "BEGIN: Download projects"
cd $LOCAL_TMP_DIR
git clone -b $branch $PROJECT_GIT_DIR
log "FINSIH: Download projects"

# 替换配置文件
log "BEGIN: Replace the configuration directory"
for CONFIG_DIR in ${CONFIG_DIRS[@]}
do
  unset template_dir
  unset config_dir
  template_dir_and_config_dir=(${CONFIG_DIR//:/ })
  template_dir=${template_dir_and_config_dir[0]}
  config_dir=${template_dir_and_config_dir[1]}
  if [[ "${template_dir##/tmp/}" != "${template_dir}" ]]; then
    # 目录在/tmp 目录下
    rm -r -f $template_dir
  else
    exit -2
  fi
  log "info: Replace $config_dir -> $template_dir"
  cp -r $config_dir $template_dir
done
log "FINISH: Replace the configuration directory"


log "BEGIN: Upload projects"
cd $LOCAL_TMP_DIR
for d in */ ; do
  project_name=`basename ${d}`
  mkdir -p $LOCAL_TMP_DIR/${project_name}/data
  mkdir -p $LOCAL_TMP_DIR/${project_name}/data/result
  mkdir -p $LOCAL_TMP_DIR/${project_name}/data/sql_files
  cp $LOCAL_TMP_DIR/${project_name}/contrib/sql_files/* $LOCAL_TMP_DIR/${project_name}/data/sql_files
  mkdir -p $LOCAL_TMP_DIR/${project_name}/data/tmp
  tar -jcf ${project_name}.tar.bz2 $d
  scp ${project_name}.tar.bz2 $deploy_host:/tmp
  ssh $deploy_host "rm -r -f /tmp/${project_name}"
  ssh $deploy_host "tar xf /tmp/${project_name}.tar.bz2 -C /tmp"
  ssh $deploy_host "cd /tmp/${project_name} && python3 setup.py sdist"
  ssh $deploy_host "cd /tmp/${project_name}/dist && sudo pip3 install *gz"
done

cd $LOCAL_TMP_DIR
for d in */ ; do
  project_name=`basename ${d}`
  ssh $deploy_host "rm -r -f ${remote_project_home}/${project_name}"
  ssh $deploy_host "mv /tmp/${project_name} ${remote_project_home}"
  ssh $deploy_host "ln -sf ${remote_project_home}/${project_name}  $remote_airflow_home/dags/"
done
log "FINISH: Upload projects"

