import csv
import argparse


parser = argparse.ArgumentParser(description='Analyze the bucket analytics report')
parser.add_argument('--csv-file', required=True)
args = parser.parse_args()

# return (older_than, younger_than)
# (-1, 99999) means ALL
# (730, 9999) means older than 2 years
def days_range(object_age):
    if object_age == 'ALL':
        return (-99999, 99999)
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

def latest_report():
    pass

with open(args.csv_file) as f:
    report = csv.DictReader(f, skipinitialspace=True)
    for item in report:
        #print(days_range(item['ObjectAge']))
        print(item['Date'])

