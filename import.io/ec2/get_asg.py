import json
import subprocess

with open("asg.log") as jsonfile:
    asgroups = json.load(jsonfile)

for asg in asgroups['AutoScalingGroups']:
    print(f'{asg["AutoScalingGroupName"]},{asg["MinSize"]},{asg["MaxSize"]},', flush=True, end='')
    if 'LaunchConfigurationName' in asg.keys():
        lc = asg['LaunchConfigurationName']
        subprocess.run("./lc_insttype.sh "+lc, shell=True)
