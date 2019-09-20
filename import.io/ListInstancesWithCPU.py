# Find all running instances by tag Proj or SecurityUpdate
# foreach instance:
# - Stop instance
# - Take ami image
# - add tag

import argparse
import sys
import boto3
import datetime, time

def tagpair(args):
    # TODO generic tag
    if (not args.proj) == (not args.batch):
        print("--proj and --batch can have one and only one", file=sys.stderr)
        return None, None

    if args.proj:
        return "tag:Proj", args.proj
    
    if args.batch:
        return "tag:SecurityUpdate", args.batch
    
    return None, None

# Stop instances, create backup images, and then start instances
def prepare(instances):
    print("\nstopping all instances...")
    instances.stop()

    images = []
    print('\nchecking instance stopped and then creating image...')
    for inst in instances:
        print(inst.instance_id, end='', flush=True)
        inst.wait_until_stopped()
        imgname = "Backup " + str(datetime.date.today()) + " " + inst.instance_id
        print(f" is {inst.state['Name']}, creating image '{imgname}'")
        image = inst.create_image(Name=imgname)
        images.append(image)

    print("\nchecking images...")
    n = 0
    for image in images:
        print(image.name, end='', flush=True)
        # give it 2 hours for image to become available
        while n <= 480 and image.state == 'pending':
            print('.', end='', flush=True)
            time.sleep(15)
            n = n + 1
            image.reload()
        if image.state == 'available':
            print(" is available")
        else:
            print(f" failed after {n/4} minutes: {image.state}")

    print("\nstarting all instance...")
    instances.start()

    print('\nchecking instances running...')
    n = 0
    for inst in instances:
        print(inst.instance_id, end='', flush=True)
        # Give them 10 minutes to get ready. Don't need to check after
        inst.wait_until_running()
        while n < 40 and inst.state['Name'] == 'pending':
            print('.', end='', flush=True)
            time.sleep(15)
            inst.reload()
        print(f" is {inst.state['Name']}")


def instanceName(instance):
    if instance.tags:
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                return tag['Value']
    return ''


def getStatistics(metric, instanceId, statistics):
    today = datetime.datetime.today()
    response = metric.get_statistics(
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': instanceId
            },
        ],
        StartTime=today - datetime.timedelta(days=30),
        EndTime=today,
        Period=86400*31,
        Statistics=[statistics, ],
        Unit='Percent'
    )
    for cpu in response['Datapoints']:
        if statistics in cpu:
            return round(cpu[statistics], 1)
    return 0

def getCPU(cloudwatch, instanceId):
    metrics = cloudwatch.metrics.filter(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': instanceId
            },
        ]
    )
    cpuavg=cpumax=0
    for metric in metrics:
        cpuavg = getStatistics(metric, instanceId, 'Average')
        cpumax = getStatistics(metric, instanceId, 'Maximum')

    return cpuavg, cpumax
#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='List all instances with CPU utilization')
parser.add_argument('--aws-profile', default='connotate')
parser.add_argument('--running-only', action='store_true')
parser.add_argument('--no-cpu', action='store_true')
parser.add_argument('--vpc-id')
args = parser.parse_args()


#
# Session
#
session = boto3.session.Session(profile_name=args.aws_profile)
ec2 = session.resource('ec2')
cloudwatch = session.resource('cloudwatch')

#instances = ec2.instances.all()
# Add filters based on argument condition
filters = []
if args.running_only:
    filters.append(
        {
            "Name": "instance-state-name",
            "Values": ['running']
        }
    )
if args.vpc_id:
    filters.append(
        {
            "Name": "vpc-id",
            "Values": [args.vpc_id]
        }
    )

instances = ec2.instances.filter(Filters=filters)

print("Instance State,Instance Type,Instance Name,Instance ID,CPU AVG, CPU MAX")
for inst in instances:
    if args.no_cpu:
        cpuavg, cpumax = '',''
    else:
        cpuavg, cpumax = getCPU(cloudwatch, inst.instance_id)
    print(f"{inst.state['Name']},{inst.instance_type},{instanceName(inst)},{inst.instance_id},{cpuavg},{cpumax}")


