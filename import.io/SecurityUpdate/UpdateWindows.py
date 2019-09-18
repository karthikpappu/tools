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
        timestamp = datetime.datetime.now().isoformat(timespec='minutes').replace(':', '') 
        imgname = f"Backup {timestamp} {inst.instance_id}"
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

# Use SSM to send command to install windows updates
# only install CriticalUpdates,SecurityUpdates Critical 7 days
def update_windows(session, tagname, tagvalues):
    ssm = session.client('ssm')
    print('\nsending ssm command...')
    response = ssm.send_command(
        DocumentName='AWS-InstallWindowsUpdates',
        DocumentVersion='1',
        Targets=[
            {
                'Key':tagname, 
                "Values":tagvalues
            }
        ],
        Parameters={
            "Action":["Install"],
            "AllowReboot":["True"],
            "IncludeKbs":[""],
            "ExcludeKbs":[""],
            "Categories":["CriticalUpdates,SecurityUpdates"],
            "SeverityLevels":["Critical"],
            "PublishedDaysOld":["7"],
            "PublishedDateAfter":[""],
            "PublishedDateBefore":[""]
        },
        TimeoutSeconds=600,
        MaxConcurrency="50",
        MaxErrors="0",
        OutputS3BucketName="yduconnotate",
        OutputS3KeyPrefix="SecurityUpdate201906/",
        CloudWatchOutputConfig={
            "CloudWatchOutputEnabled":True,
            "CloudWatchLogGroupName":"SecurityUpdate201906"
        }
    )

    command_id = response['Command']['CommandId']
    command = response['Command']
    print("Command ID: " + command_id, end='', flush=True)
    # wait no more than 50*5 seconds
    n = 0
    while n < 30 and command['Status'] == 'Pending':
        print('.', end='', flush=True)
        time.sleep(5)
        try:
            response = ssm.list_commands(CommandId=command_id)
            command = response['Commands'][0]
            print(' is ' + command['Status'])
        except Exception as e:
            print(e)

    # TODO: how to find targets?
    # InstanceIds doesn't contain the valid targets
    #print("  Targets: " + str(command['InstanceIds']))
    print(f"{command['TargetCount']} targets are updating")

    # TODO: add tags to instances to indicate the work


#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='Prepare instance for update')
parser.add_argument('--vpc-id', default='vpc-72f4a717')
parser.add_argument('--aws-profile', default='Connotate')
parser.add_argument('--proj', action='append')
parser.add_argument('--batch', action='append')
parser.add_argument('--bare-update', action='store_true')
args = parser.parse_args()

tagname, tagvalues = tagpair(args)
if (not tagname) or (not tagvalues):
    sys.exit(1)

print(tagname, tagvalues, str(datetime.datetime.now()))


#
# Session
#
session = boto3.session.Session(profile_name=args.aws_profile)
ec2 = session.resource('ec2')

instances = ec2.instances.filter(
    Filters=[
        {
            "Name": tagname,
            "Values": tagvalues
        }
    ]
)

print(f"Listing all instances...")
cnt = 0
for inst in instances:
    cnt += 1
    # TODO iam
    iam = inst.iam_instance_profile
    print(f"{inst.instance_id} is {inst.state['Name']}. IAM: {iam['Arn'] if iam else None}")
print(f"{cnt} instances are counted")


if not args.bare_update:
    prepare(instances)


update_windows(session,tagname,tagvalues)