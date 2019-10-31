
import argparse
import sys
import boto3
from multiprocessing import Pool

# multi-processing

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

def format_size(size):
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
    return size_fmt

def print_row(name, nobj, size, creation, modified, has_lifecycle, outfile=None):
    'print a csv row'
    # Format has_lifecycle
    if type(has_lifecycle) is not bool:
        lifecycle_fmt = has_lifecycle # the head
    elif has_lifecycle:
        lifecycle_fmt = 'Yes'
    else:
        lifecycle_fmt = 'No'

    print(f'{name},{nobj},{size},{creation},{modified},{lifecycle_fmt}', file=outfile)

#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='Walk through all s3 buckets for stats')
parser.add_argument('--aws-profile', default='default')
parser.add_argument('--buckets-file', default="allbuckets.log")
args = parser.parse_args()


#
# Session
#
session = boto3.session.Session(profile_name=args.aws_profile)
s3 = session.resource('s3')

def stat_bucket_task(bucketname):
    hasLc = has_lifecycle(s3, bucketname)
    bucket = s3.Bucket(bucketname)
    name, nobj, size, t0, t99 = bucket_stat(bucket)
    outname = 'csv/' + bucketname + '.csv'
    print_row(name, nobj, size, t0,t99, hasLc, outfile=open(outname, 'w'))

with open(args.buckets_file) as log:
    allbuckets = log.readlines()
    allbuckets = [ x.strip() for x in allbuckets]

with Pool(16) as p:
    p.map(stat_bucket_task, allbuckets)
