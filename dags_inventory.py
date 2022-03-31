from email.mime import image
import sys
import os
import json
from subprocess import Popen, PIPE
from prettytable import PrettyTable
import logging
from bs4 import BeautifulSoup, Tag
import smtplib
from email.message import EmailMessage
from datetime import datetime
import re


SECRET_KEY = sys.argv[1]
repo_name = sys.argv[2]
recipient_list = sys.argv[3]
region = 'us-south'

red = '\033[1;31m'
green = '\033[1;32m'
yellow = '\033[1;33m'
blue = '\033[1;34m'
end_color = '\033[0m'

pwd = os.getcwd()


all_dags_data = {}


def cmd_execute(cmd):
    cmd_result = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    cmd_output, cmd_error = cmd_result.communicate()
    returnCode = cmd_result.returncode
    cmd_output = cmd_output.decode('utf8')
    cmd_error = cmd_error.decode('utf8')
    return returnCode, cmd_output, cmd_error

def change_dir(repo_path, branch):
    dags_dir = 'dags'
    dags_path = os.path.join(repo_path,dags_dir)
    os.chdir(dags_path)
    os.system(f'git checkout {branch}')
    all_dir_files = os.listdir()
    return all_dir_files

def get_variable_name(variable_str, pod_name, cluster_variables, cluster_name):
    c_varibles = cluster_variables[cluster_name]['variables']
    c_varibles_keys = list(c_varibles.keys())
    image_name=variable_str
    all_matches = []
    requiredRegex = "\{{.*?\}}"
    matches = re.findall(requiredRegex, variable_str)
    for each in matches:
        all_matches.append(each.strip('{}'))
    
    for each in all_matches:
        variable_name = each.strip('{}').split('.')[-1].strip()
        if variable_name not in c_varibles_keys:
            cmd = f'kubectl exec -n airflow {pod_name} -- airflow variables get {variable_name}'
            returnCode, output, error = cmd_execute(cmd)
            if returnCode == 0:
                output = output.splitlines()
                value = output[0]
                # c_varibles.append(value)
                c_varibles[variable_name] = value
                image_name = image_name.replace(each,value)
            else:
                print(f"{red}ERROR: Failed at {cmd} Commad on {each_cluster} Cluster.{end_color}\n")
                print(error)
                sys.exit(returnCode)
        else:
            value = cluster_variables[cluster_name]['variables'][variable_name]
            image_name = image_name.replace(each,value)
    image_name = image_name.replace('{','').replace('}','')
    return image_name, c_varibles




### Login into IBM Cloud
print(f"\n{blue}--------- Logging into IBM Cloud ---------{end_color}")
login_cmd = f'ibmcloud login -r {region} --apikey {SECRET_KEY}'
print(f"Command: {login_cmd}")
login_returnCode, login_output, login_error = cmd_execute(login_cmd)

if login_returnCode == 0:
    print(f"{green}Successfully Logged in{end_color}\n")
else:
    print(f"{red}ERROR: Login Failed{end_color}\n")
    print(login_error)
    sys.exit(login_returnCode)

cluster_names = ['map-dal10-16x64-01']
cluster_info = {
    "map-dal10-16x64-01":{"variables": {}},
    "map-dal10-16x64-02":{"variables": {}},
    "map-dal10-16x64-03":{"variables": {}}
}
for each_cluster in cluster_info:
    dags_data = []
    dags_table = PrettyTable(["S.No", "DAG_Name", "Pythonfile", "Configuration File(YAML)", "Images" , "mainApplicationFile" ,"Paused"])
    if each_cluster == 'map-dal10-16x64-01':
        branch_name = 'dev'
    elif each_cluster == 'map-dal10-16x64-02':
        branch_name = 'test'
    else:
        branch_name = 'master'

    print(f"{blue}--------- {each_cluster} ---------{end_color}")
    ### Cluster Configuration
    repo_path = os.path.join(pwd, repo_name)
    all_dir_files = change_dir(repo_path, branch_name)
    cluster_config_cmd = f"ibmcloud ks cluster config --cluster {each_cluster}"
    print(f"Command: {cluster_config_cmd}")
    cc_returnCode, cc_output, cc_error = cmd_execute(cluster_config_cmd)
    if cc_returnCode == 0:
        print(f"{green}Successfully Configured {each_cluster}.{end_color}\n")
    else:
        print(f"{red}ERROR: Configured {each_cluster} is Failed.{end_color}\n")
        print(cc_error)
        sys.exit(cc_returnCode)
    

    ### Verify the Cluster configuration
    vc_cmd = "kubectl config current-context"
    print(f"Command: {vc_cmd}")
    vc_returnCode, vc_output, vc_error = cmd_execute(vc_cmd)
    if vc_returnCode == 0:
        print(f"{green}Successfully Verified {each_cluster}.{end_color}\n")
    else:
        print(f"{red}ERROR: Failed at {vc_cmd} Command on {each_cluster} Cluster.{end_color}\n")
        print(vc_error)
        sys.exit(vc_returnCode)
    

    ### Get the airflow-scheduler pod
    pod_cmd = "kubectl get pods -n airflow --output json"
    print(f"Command: {pod_cmd}")
    pod_returnCode, pod_output, pod_error = cmd_execute(pod_cmd)
    pod_name = ''
    if pod_returnCode == 0:
        json_data = json.loads(pod_output)
        for each_item in json_data['items']:
            name = each_item['metadata']['name']
            if 'airflow-scheduler' in name:
                pod_name = name
    else:
        print(f"{red}ERROR: Failed at {pod_cmd} Command for {each_cluster} Cluster.{end_color}\n")
        print(pod_error)
        sys.exit(pod_returnCode)
    

    ### List the all the variables
    variables_cmd = f"kubectl exec -n airflow {pod_name} -- airflow variables list --output json"
    print(f"Command: {variables_cmd}")
    variables_returnCode, variables_output, variables_error = cmd_execute(variables_cmd)
    all_variables = []
    if variables_returnCode == 0:
        variables_json_data = json.loads(variables_output)
        for each_var in variables_json_data:
            all_variables.append(each_var['key'])
    else:
        print(f"{yellow}Warning: Error at getting the Variables.{end_color}")


    ### List the Airflow Dags
    dags_cmd = f"kubectl exec -n airflow {pod_name} -- airflow dags list --output json"
    print(f"Command: {dags_cmd}")
    dags_returnCode, dags_output, dags_error = cmd_execute(dags_cmd)
    if dags_returnCode == 0:
        dags_json_data = json.loads(dags_output)
        dag_s_no = 1
        for each in dags_json_data:
            dag_name = each['dag_id']
            python_file = each['filepath']
            paused = each['paused']
            yaml_files = []
            images = []
            applications = []
            
            if python_file in all_dir_files:
                # print(python_file)
                with open(python_file) as file:
                    file_content = file.read()
                
                if 'kube/' in file_content:
                    all_lines = file_content.splitlines()
                    yaml_file_lines = [each_line for each_line in all_lines if 'kube/' in each_line]
                    for each_line in yaml_file_lines:
                        if "'" in each_line:
                            yaml_files.append(each_line.split("'")[1::2][0])
                        elif '"' in each_line:
                            yaml_files.append(each_line.split('"')[1::2][0])

                    for each_file in yaml_files:
                        with open(each_file, 'r') as f:
                            yam_file_content = f.read()
                        
                        ## Get the Image name
                        if 'image:' in yam_file_content:
                            all_lines = yam_file_content.splitlines()
                            image_file_lines = [each_line for each_line in all_lines if 'image:' in each_line]
                            for each_line in image_file_lines:
                                if "'" in each_line:
                                    tmp_image = each_line.split("'")[1::2][0]
                                    image_name, c_varibles = get_variable_name(tmp_image, pod_name, cluster_info, each_cluster)
                                    cluster_info[each_cluster]['variables'] = c_varibles
                                    
                                    images.append(image_name)
                                elif '"' in each_line:
                                    tmp_image = each_line.split('"')[1::2][0]
                                    image_name, c_varibles = get_variable_name(tmp_image, pod_name, cluster_info, each_cluster)
                                    cluster_info[each_cluster]['variables'] = c_varibles
                                    images.append(image_name) 
                                elif "image:" in each_line:
                                    tmp_image = each_line.split('image:')[1].strip()
                                    if '#' in tmp_image:
                                        tmp_image = tmp_image.split('#')[0].strip()
                                    image_name, c_varibles = get_variable_name(tmp_image, pod_name, cluster_info, each_cluster)
                                    cluster_info[each_cluster]['variables'] = c_varibles
                                    images.append(image_name)
                        else:
                            images = ['None']
                        
                        ## Get the  mainApplicationFile   
                        if 'mainApplicationFile:' in yam_file_content:
                            all_lines = yam_file_content.splitlines()
                            image_file_lines = [each_line for each_line in all_lines if 'mainApplicationFile:' in each_line]
                            for each_line in image_file_lines:
                                if "'" in each_line:
                                    tmp_app = each_line.split("'")[1::2][0]
                                    app_name, c_varibles = get_variable_name(tmp_app, pod_name, cluster_info, each_cluster)
                                    cluster_info[each_cluster]['variables'] = c_varibles
                                    
                                    applications.append(app_name)
                                elif '"' in each_line:
                                    tmp_app = each_line.split('"')[1::2][0]
                                    app_name, c_varibles = get_variable_name(tmp_app, pod_name, cluster_info, each_cluster)
                                    cluster_info[each_cluster]['variables'] = c_varibles
                                    applications.append(app_name) 
                                elif "mainApplicationFile:" in each_line:
                                    tmp_app = each_line.split('mainApplicationFile:')[1].strip()
                                    if '#' in tmp_image:
                                        tmp_app = tmp_image.split('#')[0].strip()
                                    app_name, c_varibles = get_variable_name(tmp_app, pod_name, cluster_info, each_cluster)
                                    cluster_info[each_cluster]['variables'] = c_varibles
                                    applications.append(app_name)
                        else:
                            applications = ['None']
                else:
                    yaml_files = ['None']
                    images = ['None']
                    applications = ['None']
            else:
                print(f"{yellow}Warning: {python_file} file not found in repo.{end_color}")
                sys.exit(1)

            # yaml_files = '\n'.join(yaml_files)
            # images = '\n'.join(images)
            dags_data.append([dag_s_no, dag_name, python_file, yaml_files, images, applications, paused])
            dags_table.add_row([dag_s_no, dag_name, python_file, yaml_files, images, applications, paused])
            dag_s_no = dag_s_no + 1
    else:
        print(f"{red}ERROR: Configured {each_cluster} is Failed.{end_color}\n")
        print(dags_error)
        sys.exit(dags_returnCode)
    
    # all_dags_data.append(dags_data)
    all_dags_data[each_cluster] = dags_data
    print(dags_table)





#### Generating HTML file for build result
soup = BeautifulSoup()
html_tag = soup.new_tag('html')
htmlheaders = soup.new_tag('head')
headertitle = soup.new_tag('title')
headertitle.append('Airflow DAGs Inventory Details')
htmlheaders.append(headertitle)
style = soup.new_tag('style', type='text/css')
style.append('body {font-family: Times New Roman}')
style.append('h3 {font-weight:bold; font-family: monospace; color:#3f038c;}')
style.append('.result_table,.result_table th,.result_table tr,.result_table td {  border: 2px solid black; border-collapse: collapse; margin-left: auto; margin-right: auto;}')

htmlheaders.append(style)

html_tag.append(htmlheaders)
soup.append(html_tag)



body_tag = soup.new_tag('body')

## add one new line
br_tag = soup.new_tag('br')
body_tag.append(br_tag)



for each_cluster_dags_data in all_dags_data:
    if each_cluster_dags_data == 'map-dal10-16x64-01':
        env_name = 'Dev'
    elif each_cluster_dags_data == 'map-dal10-16x64-02':
        env_name = 'Test'
    else:
        env_name = 'Prod'

    cluster_dags_data = all_dags_data[each_cluster_dags_data]


    ### Table1
    # create heading tag for Images Table
    center_tag = soup.new_tag('center')
    heading_tag = soup.new_tag('h3')
    heading_name = f'{env_name} Airflow Cluster DAGs Inventory'
    heading_tag.append(heading_name)
    center_tag.append(heading_tag)
    body_tag.append(center_tag)


    table = soup.new_tag('table class="result_table"')

    tr = soup.new_tag('tr style="font-weight: bold; color: white;background-color: #002db3"')

    td = soup.new_tag('td')
    td.append(" S.NO ")
    tr.append(td)

    td = soup.new_tag('td')
    td.append(" DAG Name ")
    tr.append(td)

    td = soup.new_tag('td')
    td.append(" Pythonfile ")
    tr.append(td)

    td = soup.new_tag('td')
    td.append(" Configuration File(YAML) ")
    tr.append(td)

    td = soup.new_tag('td')
    td.append(" Images ")
    tr.append(td)

    td = soup.new_tag('td')
    td.append(" mainApplicationFile ")
    tr.append(td)

    td = soup.new_tag('td')
    td.append(" Paused ")
    tr.append(td)


    table.append(tr)



    for each_row in cluster_dags_data:
        tr_tag = soup.new_tag('tr')
        for each_td in range(len(each_row)):
            td_tag = soup.new_tag('td')
            cell_data = each_row[each_td]
            if type(cell_data) == list:
                for each_sub_line in cell_data:
                    str_tag = soup.new_string(each_sub_line)
                    br_tag = soup.new_tag('br')
                    td_tag.append(str_tag)
                    td_tag.append(br_tag)
            else:
                td_tag.append(str(cell_data))
            tr_tag.append(td_tag)
        table.append(tr_tag)
    center_tag.append(table)

    body_tag.append(center_tag)
    soup.append(body_tag)


## add one new line
br_tag = soup.new_tag('br')
body_tag.append(br_tag)

br_tag = soup.new_tag('br')
body_tag.append(br_tag)


body_tag.append(center_tag)
soup.append(body_tag)


os.chdir(pwd)
html_file = f"dags_inventory.html"
with open(html_file, "w") as file:
    file.write(str(soup.prettify()))

print("\nSuccessfully Created HTML file.\n")




### Sending mail
html_file = "dags_inventory.html"
with open(html_file) as file:
    html_content = file.read()


msg = EmailMessage()
msg['From'] = 'mapfunc@us.ibm.com'
msg['Subject'] = 'Airflow DAGs Inventory'
msg['To'] = recipient_list
# msg['To'] = 'kolanu.harish@ibm.com, cunico@us.ibm.com, bbotev@bg.ibm.com, akumarr2@in.ibm.com, nagendrac@in.ibm.com, sbeeramm@in.ibm.com'
# msg['To'] = 'kolanu.harish@ibm.com, cunico@us.ibm.com, bbotev@bg.ibm.com'
# msg['Cc'] = 'souvik.dutta@ibm.com'

# msg['To'] = recipient_list
# if cc_list:
#     msg['Cc'] = cc_list


msg.add_alternative(html_content, subtype='html')
server = smtplib.SMTP('na.relay.ibm.com')
server.send_message(msg)
server.quit()
print('\nSuccessfully sent an email')


