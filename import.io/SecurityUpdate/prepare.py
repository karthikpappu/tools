# Find all running instances in VPC
# foreach instance:
# - Stop instance
# - Take ami image
# - add tag

import argparse
import sys
import boto3


#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='Prepare instance for update')
parser.add_argument('--vpc-id', default='vpc-72f4a717')
parser.add_argument('--aws-profile', default='YuantaiDu')
args = parser.parse_args()



def ListVpcs(ec2client):
    response = ec2client.describe_vpcs()
    return [ vpc['VpcId'] for vpc in response['Vpcs'] ]

def InstanceName(instance):
    if not "Tags" in instance.keys():
        return ''
    tags = instance["Tags"]
    for tag in tags:
        if tag['Key'] == 'Name':
            return tag['Value']
    return ''

def VpcId(instance):
    for inf in instance["NetworkInterfaces"]:
        return inf["VpcId"]
    return ""

def StateReason(instance):
    return instance['StateReason'] if 'StateReason' in instance.keys() else ''

# 'running', 'stopped'...
def InstanceState(instance):
    return instance["State"]["Name"]

# 'windows'
def InstancePlatform(instance):
    return instance["Platform"] if "Platform" in instance.keys() else ''

def getInstance(ec2, instance_id):
    response = ec2.describe_instances(InstanceIds=[instance_id])
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            return instance
    return None

# create image
def create_image(ec2, instance_id):
    instance = getInstance(ec2, instance_id)
    if instance == None:
        print("Can't find instance " + instance_id)
        return
    
    orig_state = InstanceState(instance)
    try:
        if orig_state != 'stopped':
            print ("Ready to stop "+instance_id)
            ec2.stop_instances(InstanceIds=[instance_id])
        #ec2.create_image(InstanceId=instance_id,
        #                      Name='Backup '+instance_id)
        if orig_state != 'stopped':
            print ("Ready to start "+instance_id)
            ec2.stop_instances(InstanceIds=[instance_id])
    except Exception as e:
        print(e)


#
# Session
#
session = boto3.session.Session(profile_name=args.aws_profile)
ec2client = boto3.client('ec2')

#TestInst = 'i-0897d04fee80c483c'
#create_image(ec2client, TestInst, 'stopped')
#sys.exit(0)

# Loop through all instances
response = ec2client.describe_instances()
for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        if VpcId(instance) == args.vpc_id:
            instance_id = instance["InstanceId"]
            print( '%s,%s,%s,%s,%s' % (instance["InstanceType"], InstanceName(instance), instance_id, InstanceState(instance), InstancePlatform(instance)))
            try:
                ec2client.create_image(InstanceId=instance_id, Name='Backup '+instance_id)
            except Exception as e:
                print (e)
