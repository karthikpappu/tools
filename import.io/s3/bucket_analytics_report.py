import csv
import argparse
import os.path, sys
import datetime


parser = argparse.ArgumentParser(description='Analyze the bucket analytics report')
parser.add_argument('--csv-file', required=True)
args = parser.parse_args()

if args.csv_file == 'print-header':
    print('Report,Storage,Retrieved,Latest Access,Median Access,ObjectAgeForSIATransition,STANDARD_IA,GLACIER,INTELLIGENT_TIERING,ONEZONE_IA')
    sys.exit(0)


def get_report(csvfile):
    report = []
    with open(csvfile) as f:
        for item in csv.DictReader(f, skipinitialspace=True):
            report.append(item)
    return report

# return (older_than, younger_than)
# (0, 9999) means ALL
# (730, 9999) means older than 2 years
def days_range(object_age):
    if object_age == 'ALL':
        return (0, 9999)
    elif object_age == '730+':
        return (730, 9999)
    else:
        days = object_age.split('-')

    try:
        if len(days) != 2:
            return None,None
        d0 = int(days[0])
        d1 = int(days[1])
        return d0, d1
    except Exception as e:
        return None, None

def younger_age(age1, age2):
    if age1 == 'ALL' or age2 == 'ALL':
        return False
    a1, b1 = days_range(age1)
    a2, b2 = days_range(age2)

    return a1 < a2

# expect "2019-09-27"
def get_date(datestr):
    datefields = datestr.split('-')
    try:
        y,m,d = map(int, datefields)
    except:
        y,m,d = 1,1,1
    return datetime.date(y,m,d)

# 1. whoever is newer report ('Date')
# 2. whoever has younger ObjectAge with the field
def later_item(item, compared, field):
    if item is None or not item[field]:
        return compared

    if compared is None:
        return item

    if get_date(item['Date']) > get_date(compared['Date']):
        #print(item)
        return item
    elif get_date(item['Date']) < get_date(compared['Date']):
        return compared

    # Now report dates are the same, then is ther field? is it younger?
    if item[field].strip() and younger_age(item['ObjectAge'], compared['ObjectAge']):
        #print(item)
        return item

    return compared

def analyze_row(item, latest_storage, latest_retrieved, latest_transition, non_standard):
    if item['StorageClass'] != 'STANDARD':
        non_standard[item['StorageClass']] = 'Y'
        return latest_storage, latest_retrieved, latest_transition, non_standard
    if item['ObjectAge'] == 'ALL':
        if latest_transition is None:
            latest_transition = item
        if get_date(item['Date']) >= get_date(latest_transition['Date']):
            if item['ObjectAgeForSIATransition'].strip():
                latest_transition = item
    else:
        latest_storage = later_item(item, latest_storage, 'Storage_MB')

        latest_retrieved = later_item(item, latest_retrieved, 'DataRetrieved_MB')

    return latest_storage, latest_retrieved, latest_transition, non_standard

def estimate_dates(item):
    starting, median = '',''
    if item:
        report_date = get_date(item['Date'])
        d1,d9 = days_range(item['ObjectAge'])
        starting = report_date - datetime.timedelta(days = d1)
        if d9 > 730:
            median = ''
        else:
            median = report_date - datetime.timedelta(days = ((d1+d9)//2))
    return starting, median

latest_storage, latest_retrieved, latest_transition = None, None, None
non_standard = {'STANDARD_IA': '', 'GLACIER': '', 'ONEZONE_IA': '', 'INTELLIGENT_TIERING': ''}
report = get_report(args.csv_file)
for item in report:
    #print(days_range(item['ObjectAge']))
    #print(item['Date'])
    #if item['Storage_MB'].strip():
    #    print(item['Storage_MB'], 'Yes')
    latest_storage, latest_retrieved, latest_transition, non_standard = \
        analyze_row(item, latest_storage, latest_retrieved, latest_transition, non_standard)

bucket_file = os.path.basename(args.csv_file)
storage = latest_storage['ObjectAge'] if latest_storage else 'NEVER'
retrieved = latest_retrieved['ObjectAge'] if latest_retrieved else 'NEVER'
retrieved_date1, retrieved_date_median = estimate_dates(latest_retrieved)
objectAgeForSIATransition = latest_transition['ObjectAgeForSIATransition'] if latest_transition else ''

# CSV Line
print(bucket_file, end='')
print(f',{storage}', end ='')
print(f',{retrieved}', end='')
print(f',{retrieved_date1}', end='')
print(f',{retrieved_date_median}', end='')
print(f',{objectAgeForSIATransition}', end='')
print(f',{non_standard["STANDARD_IA"]}', end='')
print(f',{non_standard["GLACIER"]}', end='')
print(f',{non_standard["INTELLIGENT_TIERING"]}', end='')
print(f',{non_standard["ONEZONE_IA"]}', end='')
print()

