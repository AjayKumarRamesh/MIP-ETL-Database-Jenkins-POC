import os
import sys
from subprocess import PIPE, Popen

GIT_PREVIOUS_SUCCESSFUL_COMMIT = sys.argv[1]
GIT_COMMIT = sys.argv[2]
db_username='harishk'
db_password='IbmDB2#12345678'



red='\033[1;31m'
green='\033[1;32m'
yellow='\033[1;33m'
end_color='\033[0m'


def cmd_execute(cmd):
    cmd_result = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    returnCode = cmd_result.wait()
    cmd_output, cmd_error = cmd_result.communicate()
    cmd_output = cmd_output.decode('utf8')
    cmd_error = cmd_error.decode('utf8')
    return returnCode, cmd_output, cmd_error



git_diff_cmd = f'git diff {GIT_PREVIOUS_SUCCESSFUL_COMMIT}..{GIT_COMMIT} --name-only'
git_diff_rt, git_diff_cmd_output, git_diff_cmd_error = cmd_execute(git_diff_cmd)
if git_diff_rt != 0:
    if git_diff_cmd_error:
        print(git_diff_cmd_error)
        sys.exit(1)
if git_diff_rt == 0:
    if git_diff_cmd_output:
        print(git_diff_cmd_output)