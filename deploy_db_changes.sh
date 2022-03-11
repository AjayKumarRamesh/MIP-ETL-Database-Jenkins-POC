#!/bin/bash

RED="\e[1;31m"
GREEN="\e[32m"
ENDCOLOR="\e[0m"


GIT_PREVIOUS_SUCCESSFUL_COMMIT=$1
GIT_COMMIT=$2
db_username='harishk'
db_password='IbmDB2#12345678'



git_changes=($(git diff ${GIT_PREVIOUS_SUCCESSFUL_COMMIT}..${GIT_COMMIT} --name-only))

if [ -z ${git_changes} ]; then
    echo "There is no changes for this build, so exit from the job"
    exit 1
fi 

for each_change in ${git_changes[@]}; do
    echo ${each_change}
    
done
