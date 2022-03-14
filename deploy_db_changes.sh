#!/bin/bash


GIT_PREVIOUS_SUCCESSFUL_COMMIT=$1
GIT_COMMIT=$2
db_username=$3
db_password=$4


red="\e[1;31m"
green="\e[1;32m"
yellow="\e[1;33m"
blue="\e[1;34m"
end_color="\e[0m"



## Get the updated sql files
git_changes=($(git diff ${GIT_PREVIOUS_SUCCESSFUL_COMMIT}..${GIT_COMMIT} --name-only | grep "\.sql$"))

if [ -z ${git_changes} ]; then
    echo -e "${yellow}Warning: There is no DB changes for this build.${end_color}"
    exit 0
else
    echo -e "\n${blue}Below are the updated sql files.${end_color}\n${git_changes}\n\n"
    for each_change in ${git_changes[@]}; do
        echo -e "${blue}--------- Deploying ${each_change} ---------${end_color}\n"
        liquibase update --changelog-file=${each_change} --username=${db_username} --password=${db_password}
        if [ $? == 0 ]; then
            echo -e "\n${green}${each_change} has been deployed successfully.${end_color}\n"
        else
            echo -e "\n${red}Failed to deploy ${each_change} ${end_color}\n"
        fi
    done
fi 


