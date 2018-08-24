#!/bin/bash

export REPO_HOME=$(pwd)
export BUILD_DIR=${REPO_HOME}/build
export WORK_DIR=${REPO_HOME}/.tmp

# Fetch reusable functions ...
source ${BUILD_DIR}/functions.sh
# Fetch constants and environment variables ...
source ${BUILD_DIR}/env.sh

export args=$*

write_log "Arguments --> ${args}"

write_log "################### Cleanup #####################"

write_log "Work Directory --> ${WORK_DIR}"
run_cmd "rm -rf ${WORK_DIR}"
run_cmd "mkdir ${WORK_DIR}"

#Place as many pre-requisite steps here as requires...
write_log "#################### Install Requisite Packages ###############"

write_log " ----------- 1. Install Tableau SDK ------------- "

run_cmd "cd ${WORK_DIR}"
run_cmd "wget ${TABLEAU_URL}"
run_cmd "tar -xvf ${TABLEAU_TAR_BALL}"
run_cmd "export TABLEAU_DIR=$(ls | grep Tableau | grep -v gz)"
run_cmd "cd ${TABLEAU_DIR}"
run_cmd "python setup.py install"
run_cmd "cd ${REPO_HOME}"

write_log "####################  Install PPExtensions ####################"

run_cmd "pip install ppextensions"

write_log "################### Final Cleanup #########################"

run_cmd "rm -rf ${WORK_DIR}"

write_log "########################  BUILD SUCCESS ###############################"

