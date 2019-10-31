
import argparse
import sys
import boto3
import csv
import datetime
from multiprocessing import Pool
from functools import reduce

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

# Map function
def object_info(obj):
    info = {
        'Small Size': 0,
        'Small Count': 0,
        'Small New': 0,
        'Small 30Days': 0,
        'Small 90Days': 0,
        'Small 1Year': 0,
        'Small 2Years': 0,
        'Large Size': 0,
        'Large Count': 0,
        'Large New': 0,
        'Large 30Days': 0,
        'Large 90Days': 0,
        'Large 1Year': 0,
        'Large 2Years': 0
    }
    age = datetime.datetime.now() - obj.last_modified.replace(tzinfo=None)
    if obj.size >= 128 * 1024:
        # Large File
        info['Large Size'] += obj.size
        info['Large Count'] += 1
        if age.days >= 730:
            info['Large 2Years'] += 1
        elif age.days >= 365:
            info['Large 1Year'] += 1
        elif age.days >= 90:
            info['Large 90Days'] += 1
        elif age.days >= 30:
            info['Large 30Days'] += 1
        else:
            info['Large New'] += 1
    else:
        # Small File
        info['Small Size'] += obj.size
        info['Small Count'] += 1
        if age.days >= 730:
            info['Small 2Years'] += 1
        elif age.days >= 365:
            info['Small 1Year'] += 1
        elif age.days >= 90:
            info['Small 90Days'] += 1
        elif age.days >= 30:
            info['Small 30Days'] += 1
        else:
            info['Small New'] += 1
    return info

# Reduce function
def reduce_info(info1, info2):
    info = {}
    for key in info1.keys():
        info[key] = info1[key] + info2[key]
    return info

#
def bucket_stat(bucket):
    objinfos = []
    for obj in bucket.objects.all():
        oinfo = object_info(obj)
        objinfos.append(oinfo)
    bucketinfo = reduce(reduce_info, objinfos)

    return [bucketinfo]

def bucket_stat_mp(bucket):
    p = Pool(processes=16)
    objinfos = p.imap(object_info, bucket.objects.all())
    bucketinfo = reduce(reduce_info, objinfos)

    return bucketinfo

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

def write_csv(csv_dicts, csvoutfile):
    if not csv_dicts:
        return
    with open(csvoutfile, 'w') as outfile:
        dwriter = csv.DictWriter(outfile, csv_dicts[0].keys())
        dwriter.writeheader()
        dwriter.writerows(csv_dicts)
#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='Walk through all s3 buckets for stats')
parser.add_argument('--aws-profile', default='default')
parser.add_argument('bucket')
args = parser.parse_args()


#
# Session
#
session = boto3.session.Session(profile_name=args.aws_profile)
s3 = session.resource('s3')

def stat_bucket_task(bucketname):
    bucket = s3.Bucket(bucketname)
    bucket_info = bucket_stat(bucket)
    outname = bucketname + '.csv'
    write_csv(bucket_info, outname)

stat_bucket_task(args.bucket)
