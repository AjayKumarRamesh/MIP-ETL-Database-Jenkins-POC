#!/bin/bash

RED="\e[1;31m"
GREEN="\e[1;32m"
YELLOW="\e[1;33m"
ENDCOLOR="\e[0m"


GIT_PREVIOUS_SUCCESSFUL_COMMIT=$1
GIT_COMMIT=$2
db_username='harishk'
db_password='IbmDB2#12345678'


## Get the updated DDL files
git_changes=($(git diff ${GIT_PREVIOUS_SUCCESSFUL_COMMIT}..${GIT_COMMIT} --name-only | grep *.sql))

if [ -z ${git_changes} ]; then
    echo -e "${YELLOW}Warning: There is no DB changes for this build, so exit from the job ${ENDCOLOR}"
fi 

for each_change in ${git_changes[@]}; do
    echo ${each_change}
    liquibase status
    
done
