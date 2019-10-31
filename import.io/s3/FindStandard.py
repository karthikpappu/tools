import argparse
import sys
import boto3
import smtplib
import datetime
from email.message import EmailMessage

#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='Walk through the bucket to find all standard class')
parser.add_argument('bucket')
parser.add_argument('--aws-profile', default='default')
args = parser.parse_args()


#
# Session
#
session = boto3.session.Session(profile_name=args.aws_profile)
s3 = session.resource('s3')

bucket = s3.Bucket(args.bucket)
csvfile=args.bucket + "_STANDARD.csv"
with open(csvfile, 'w') as f:
    print('Storage Class,File Name,Modified,Size', file=f, flush=True)
    count = 0
    for obj in bucket.objects.all():
      try:
        count += 1
        if count % 10000 == 0:
            print('\tcounted',count,str(datetime.datetime.now()), file=f, flush=True)
        if obj.storage_class == 'STANDARD':
            print(f'{obj.storage_class},{obj.key},{obj.last_modified},{obj.size}', file=f, flush=True)
      except Exception as e:
        print(e, file=f, flush=True)
#with open(csvfile) as f:
#    msg = EmailMessage()
#    msg.set_content(f.read())

#msg['Subject'] = 'Scan result of ' + args.bucket
#msg['From'] = 'smtp@localhost'
#msg['To'] = 'yuantai.du@import.io'

#s = smtplib.SMTP('localhost')
#s.send_message(msg)
#s.quit()
