#!/bin/sh


GIT_PREVIOUS_SUCCESSFUL_COMMIT=$1
GIT_COMMIT=$2
db_username='harishk'
db_password='IbmDB2#12345678'

red="\e[1;31m"
green="\e[1;32m"
yellow="\e[1;33m"
end_color="\e[0m"



## Get the updated sql files
git_changes=($(git diff ${GIT_PREVIOUS_SUCCESSFUL_COMMIT}..${GIT_COMMIT} --name-only | grep "\.sql$"))

if [ -z ${git_changes} ]; then
    echo -e "${yellow}Warning: There is no DB changes for this build.${end_color}"
else
    for each_change in ${git_changes[@]}; do
        echo ${each_change}
        liquibase status --changelog-file=${each_change}
    done
fi 


