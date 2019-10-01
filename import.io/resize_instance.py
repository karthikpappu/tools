
# Find all running instances by tag Proj or SecurityUpdate
# foreach instance:
# - Stop instance
# - Take ami image
# - add tag

import argparse
import sys
import boto3
import datetime, time


def instanceName(instance):
    if instance.tags:
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                return tag['Value']
    return ''

def stop_instance(instance, dryrun=False):
    print("\nstopping instance...")
    if dryrun:
        return
    instance.stop()
    instance.wait_until_stopped()

def create_image(inst, dryrun=False):
    print(inst.instance_id, end='', flush=True)
    timestamp = datetime.datetime.now().isoformat(timespec='minutes').replace(':', '')
    imgname = f"Backup {timestamp} {inst.instance_id} {instanceName(inst)}"
    print(f" is {inst.state['Name']}, creating image '{imgname}'")
    if dryrun:
        print ("Dryrun: ami-dryrun")
        return 'ami-dryrun'

    image = inst.create_image(Name=imgname)

    print(f"\nchecking image {image.id}...")
    n = 0
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
    return image.image_id

def create_instance(ec2, instance, imageId, new_type, count, dryrun=False):
    print("\ncreating instance...")
    sg_ids = [g['GroupId'] for g in instance.security_groups]
    print(f"ImageId={imageId},InstanceType={new_type},KeyName={instance.key_name},count={count},subnetId={instance.subnet_id}")
    if dryrun:
        print(f"New Instances:", ['i-deadbeef']*count)
        return ['i-deadbeef']*count
    kwarg = {
        'ImageId': imageId,
        'InstanceType': new_type,
        'KeyName': instance.key_name,
        'MaxCount': count,
        'MinCount': count,
        'TagSpecifications': [
            {
                'ResourceType': 'instance',
                'Tags': instance.tags
            }
        ],
        'NetworkInterfaces': [
            {
                'DeviceIndex': 0,
                'Groups': sg_ids,
                'SubnetId': instance.subnet_id
            }
        ]
    }

    if new_type.startswith(('t', 'T')):
        kwarg ['CreditSpecification'] = {
            'CpuCredits': 'unlimited'
        }

    if instance.iam_instance_profile is not None:
        kwarg['IamInstanceProfile'] = {
            'Arn': instance.iam_instance_profile['Arn'],
        }

    instances = ec2.create_instances(**kwarg)

    newIds = [inst.instance_id for inst in instances]
    print(f"New Instances:", newIds)
    return newIds


#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='Resize instance ')
parser.add_argument('--aws-profile', default='connotate')
parser.add_argument('--instance-id', required=True, help='For test, use i-0897d04fee80c483c for AdminServer')
parser.add_argument('--new-type', required=True)
parser.add_argument('--image-id', help='If image id is provided, then it will skip stopping instance and creating image')
parser.add_argument('--count', type=int, default=1)
parser.add_argument('--dryrun', action='store_true')
args = parser.parse_args()

print(args.instance_id, '->', args.new_type, str(datetime.datetime.now()))


#
# Session
#
session = boto3.session.Session(profile_name=args.aws_profile)
ec2 = session.resource('ec2')

instance = ec2.Instance(args.instance_id)

#newinst = create_instance(ec2, instance, 'ami-0142e7bc9c8b9de0a', args.new_type, args.count)
#sys.exit(0)

imageId = args.image_id
if imageId is None:
    stop_instance(instance, args.dryrun)
    imageId = create_image(instance, args.dryrun)

newinst = create_instance(ec2, instance, imageId, args.new_type, args.count, args.dryrun)


