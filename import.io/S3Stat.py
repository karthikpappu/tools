
import argparse
import sys
import boto3
import datetime, time


# check if bucket has set lifecycle policy
def has_lifecycle(s3, bucketName):
    lcconfig = s3.BucketLifecycleConfiguration(bucketName)
    has = False
    try:
        has = len(lcconfig.rules) > 0
    except Exception as e:
        has = False
    return has

#
def bucket_stat(bucket):
    # TODO
    name = bucket.name
    creation = bucket.creation_date
    size = 0
    last = bucket.creation_date
    nobj = 0
    for obj in bucket.objects.all():
        nobj += 1
        size += obj.size
        if last < obj.last_modified:
            last = obj.last_modified
    return name, nobj, size, creation, last

def print_row(name, nobj, size, creation, modified, has_lifecycle):
    'print a csv row'
    # Format size
    kB = 1024
    MB = 1024 * 1024
    GB = 1024 * 1024 * 1024
    TB = 1024 * 1024 * 1024 * 1024
    if type(size) is not int:
        size_fmt = size # the head
    elif size >= TB:
        size_fmt = f'{round(size/TB, 1)}TB'
    elif size >= GB:
        size_fmt = f'{round(size/GB, 1)}GB'
    elif size >= MB:
        size_fmt = f'{round(size/MB, 1)}MB'
    elif size >= kB:
        size_fmt = f'{round(size/kB, 1)}kB'
    else:
        size_fmt = str(size)+'B'

    # Format has_lifecycle
    if type(has_lifecycle) is not bool:
        lifecycle_fmt = has_lifecycle # the head
    elif has_lifecycle:
        lifecycle_fmt = 'Yes'
    else:
        lifecycle_fmt = 'No'

    print(f'{name},{nobj},{size_fmt},{creation},{modified},{lifecycle_fmt}')

#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='Walk through all s3 buckets for stats')
parser.add_argument('--aws-profile', default='connotate')
args = parser.parse_args()


#
# Session
#
session = boto3.session.Session(profile_name=args.aws_profile)
s3 = session.resource('s3')

print_row('Bucket Name', '#Objects', 'Bucket Size', 'Creation Date', 'Last Modified', 'Has Lifecycle')
for bucket in s3.buckets.all():
    hasLc = has_lifecycle(s3, bucket.name)
    name, nobj, size, t0, t99 = bucket_stat(bucket)
    print_row(name, nobj, size, t0,t99, hasLc)
