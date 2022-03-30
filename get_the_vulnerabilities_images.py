import json
from operator import imod
import sys
from subprocess import Popen, PIPE
from prettytable import PrettyTable
import logging
from bs4 import BeautifulSoup, Tag
import smtplib
from email.message import EmailMessage
from datetime import datetime


SECRET_KEY = sys.argv[1]
recipient_list = sys.argv[2]

region = 'us-south'


red = '\033[1;31m'
green = '\033[1;32m'
yellow = '\033[1;33m'
blue = '\033[1;34m'
end_color = '\033[0m'

images_table = PrettyTable(["S.No", "Repository@Digest", "Tag", "Namespace", "Created", "Size", "Security status"])
vulnerability_table = PrettyTable(["S.No", 'Vulnerability_ID', "Summary", "Count of Images with this vulnerability", "Images with this vulnerability"])

images_data = []
vulnerability_data = []
vulnerability_data_dict = {}

def human_readable_size(size, decimal_places=3):
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            break
        size /= 1024
    return f"{size:.{decimal_places}f} {unit}"

def cmd_execute(cmd):
    cmd_result = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    cmd_output, cmd_error = cmd_result.communicate()
    returnCode = cmd_result.returncode
    cmd_output = cmd_output.decode('utf8')
    cmd_error = cmd_error.decode('utf8')
    return returnCode, cmd_output, cmd_error


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


## Get the cluster vulnerabilities images
namespace = 'map-dev-namespace'
images_cmd = f'ibmcloud cr images --restrict {namespace} --format "{{{{ .Repository }}}}@@{{{{ .Digest }}}}@@{{{{ .Tag }}}}@@{{{{ .Created }}}}@@{{{{ .Size }}}}@@{{{{ .SecurityStatus.Status }}}}"'
print(f"Command: {images_cmd}")
images_returnCode, images_output, images_error = cmd_execute(images_cmd)
if images_returnCode == 0:
    if images_output:
        all_lines = images_output.splitlines()
        all_images = []
        issues = []
        count = 1
        vulnerability_IDs = []
        for each_line in all_lines:
            line_data = each_line.split('@@')

            image_name = line_data[0].strip()
            digest = line_data[1].strip()
            repository_digest = f"{image_name}@{digest}"

            image_tag = line_data[2].strip()

            c_date = int(line_data[3].strip())
            created = datetime.fromtimestamp(c_date).strftime("%Y/%m/%d")

            size = line_data[4].strip()
            size = human_readable_size(int(size))

            num_of_issues = line_data[5].strip()
            if   'unsupported' in num_of_issues.lower() or 'no' in num_of_issues.lower():
                continue
            images_table.add_row([count, repository_digest, image_tag, namespace, created, size, num_of_issues])
            images_data.append([count, repository_digest, image_tag, namespace, created, size, num_of_issues])

            count = count + 1

            
            
            va_cmd = f'ibmcloud cr va {image_name}:{image_tag} --output json'
            # print(f"Command: {va_cmd}")
            va_returnCode, va_output, va_error = cmd_execute(va_cmd)
            if va_returnCode == 0:
                data = va_output[1:-2]
                json_data = json.loads(data)
                for each_va in json_data['vulnerabilities']:
                    for each_sn in each_va['security_notices']:
                        v_id = each_va['cve_id']
                        summary = each_sn['summary']
                        all_v_ids = list(vulnerability_data_dict.keys())
                        if v_id in all_v_ids:
                            temp_v_data = vulnerability_data_dict[v_id]
                            vulnerability_data_dict[v_id]['count'] = temp_v_data['count'] + 1
                            temp_images_data = temp_v_data['images']
                            temp_images_data.append(f"{image_name}:{image_tag}")
                            vulnerability_data_dict[v_id]['images'] = temp_images_data
                        else:
                            temp_v_data = {}
                            temp_v_data['summary'] = summary
                            temp_v_data['count'] = 1
                            temp_image_data = f"{image_name}:{image_tag}"
                            temp_v_data['images'] =  [temp_image_data]
                        vulnerability_data_dict[v_id] = temp_v_data

            else:
                print(f'{red}\nERROR: Failed to execute "{va_cmd}" Command.{end_color}\n')
                print(va_error)
                sys.exit(va_returnCode)

else:
    print(f'{red}\nERROR: Failed to execute "ibmcloud cr images" Command.{end_color}\n')
    print(images_error)
    sys.exit(images_returnCode)


v_s_num = 1 
for v_id in vulnerability_data_dict:
    summary = vulnerability_data_dict[v_id]['summary']
    v_count = vulnerability_data_dict[v_id]['count']
    images = vulnerability_data_dict[v_id]['images']


    vulnerability_data.append([v_s_num ,v_id, summary, v_count, images])
    vulnerability_table.add_row([v_s_num ,v_id, summary, v_count, images])
    v_s_num = v_s_num + 1




# print(images_data)
# print(vulnerability_data)

print(images_table)
# print()
# print(vulnerability_table)

# sys.exit()




#### Generating HTML file for build result
soup = BeautifulSoup()
html_tag = soup.new_tag('html')
htmlheaders = soup.new_tag('head')
headertitle = soup.new_tag('title')
headertitle.append('Image Vulnerabilities Details')
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


### Table1
# create heading tag for Images Table
center_tag = soup.new_tag('center')
heading_tag = soup.new_tag('h3')
heading_tag.append('IBM Cloud Container Registry Images with issues')
center_tag.append(heading_tag)
body_tag.append(center_tag)


table = soup.new_tag('table class="result_table"')

tr = soup.new_tag('tr style="font-weight: bold; color: white;background-color: #002db3"')

td = soup.new_tag('td')
td.append(" S.NO ")
tr.append(td)

td = soup.new_tag('td')
td.append(" Repository@Digest ")
tr.append(td)

td = soup.new_tag('td')
td.append(" Tag ")
tr.append(td)

td = soup.new_tag('td')
td.append(" Namespace ")
tr.append(td)

td = soup.new_tag('td')
td.append(" Created ")
tr.append(td)

td = soup.new_tag('td')
td.append(" Size ")
tr.append(td)

td = soup.new_tag('td')
td.append(" Security Status ")
tr.append(td)

table.append(tr)


for each_row in images_data:
    tr_tag = soup.new_tag('tr')
    for each_td in range(len(each_row)):
        td_tag = soup.new_tag('td')
        td_tag.append(str(each_row[each_td]))
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

### Table2
# create heading tag for Vulnerabilities Table
center_tag = soup.new_tag('center')
heading_tag = soup.new_tag('h3')
heading_tag.append('Vulnerability Details')
center_tag.append(heading_tag)
body_tag.append(center_tag)


table = soup.new_tag('table class="result_table"')

tr = soup.new_tag('tr style="font-weight: bold; color: white;background-color: #002db3"')

td = soup.new_tag('td')
td.append(" S.NO ")
tr.append(td)

td = soup.new_tag('td')
td.append(" Vulnerability_ID ")
tr.append(td)

td = soup.new_tag('td')
td.append(" Summary ")
tr.append(td)

td = soup.new_tag('td')
td.append(" Count of Images with this vulnerability ")
tr.append(td)

td = soup.new_tag('td')
td.append(" Images with this vulnerability ")
tr.append(td)

table.append(tr)


for each_row in vulnerability_data:
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


html_file = f"images_details.html"
with open(html_file, "w") as file:
    file.write(str(soup.prettify()))

print("\nSuccessfully Created HTML file.\n")



### Sending mail
html_file = "images_details.html"
with open(html_file) as file:
    html_content = file.read()


msg = EmailMessage()
msg['From'] = 'mapfunc@us.ibm.com'
msg['Subject'] = 'IBM Cloud Container Registry Images Details'
# msg['To'] = 'kolanu.harish@ibm.com, bbotev@bg.ibm.com, akumarr2@in.ibm.com, nagendrac@in.ibm.com, sbeeramm@in.ibm.com'
# msg['To'] = 'kolanu.harish@ibm.com, cunico@us.ibm.com, bbotev@bg.ibm.com'
# msg['Cc'] = 'souvik.dutta@ibm.com'

msg['To'] = recipient_list
# if cc_list:
#     msg['Cc'] = cc_list


msg.add_alternative(html_content, subtype='html')
server = smtplib.SMTP('na.relay.ibm.com')
server.send_message(msg)
server.quit()
print('\nSuccessfully sent an email')

