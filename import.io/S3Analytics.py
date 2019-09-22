import argparse
import sys
import boto3


def all_buckets(client):
    try:
        response = client.list_buckets()
        return response['Buckets']
    except Exception as e:
        print(e)
        return []

def has_analytics(client, bucketname, analytics_id='storage_analysis'):
    try:
        client.get_bucket_analytics_configuration(Bucket=bucketname, Id=analytics_id)
        return True
    except Exception as e:
        return False

def add_analytics(client, bucketname, analytics_id='storage_analysis', saveto='s3-storage-analysis-temporary'):
    saveto_bucket = 'arn:aws:s3:::'+saveto
    try:
        client.put_bucket_analytics_configuration(
            Bucket=bucketname,
            Id=analytics_id,
            AnalyticsConfiguration={
                'Id' : analytics_id,
                'StorageClassAnalysis': {
                    'DataExport': {
                        'OutputSchemaVersion': 'V_1',
                        'Destination': {
                            'S3BucketDestination': {
                                'Format': 'CSV',
                                'Bucket': saveto_bucket
                            }
                        }
                    }
                }
            }
        )
    except Exception as e:
        print(e)

#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='Walk through all s3 buckets for stats')
parser.add_argument('--aws-profile', default='default')
parser.add_argument('--analytics-id', default='storage_analysis')
parser.add_argument('--saveto-bucket', default='s3-storage-analysis-temporary')
args = parser.parse_args()


#
# Session
#
session = boto3.session.Session(profile_name=args.aws_profile)
s3c = session.client('s3')

buckets = all_buckets(s3c)
for bucket in buckets:
    print(bucket['Name'], args.analytics_id, end='')
    if has_analytics(s3c, bucket['Name'], analytics_id=args.analytics_id):
        print(' exists')
    else:
        add_analytics(s3c, bucket['Name'], analytics_id=args.analytics_id, saveto=args.saveto_bucket)
        print(' is added')
