import csv

def get_csv(csvfile):
    csvdict = []
    with open(csvfile) as f:
        for item in csv.DictReader(f, skipinitialspace=True):
            csvdict.append(item)
    return csvdict

def get_report_row(bucket, csv2):
    for row in csv2:
        if row['Report'].startswith(bucket):
            return row
    return None

def convertSize(sizestr):
    if sizestr.endswith('TB'):
        return int(float(sizestr[:-2]) * 1024**4)
    elif sizestr.endswith('GB'):
        return int(float(sizestr[:-2]) * 1024**3)
    elif sizestr.endswith('MB'):
        return int(float(sizestr[:-2]) * 1024**2)
    elif sizestr.endswith('kB'):
        return int(float(sizestr[:-2]) * 1024**2)
    elif sizestr.endswith('B'):
        return int(sizestr[:-1])
    else:
        return int(sizestr)
    return 0

csvfile1 = 'ImportS3Buckets.csv'
csvfile2 = 'buckets.csv'
csvoutfile = 'combined.csv'

csv1 = get_csv(csvfile1)
csv2 = get_csv(csvfile2)

empty_csv2_row = csv2[0].copy()
for key in empty_csv2_row:
    empty_csv2_row[key] = ''

for row in csv1:
    bucket = row['Bucket Name']
    row2 = get_report_row(bucket, csv2)
    if row2:
        row.update(row2)
    else:
        row.update(empty_csv2_row)

    #row['Bucket Size'] = convertSize(row['Bucket Size'])

with open(csvoutfile, 'w') as outfile:
    dwriter = csv.DictWriter(outfile, csv1[0].keys())
    dwriter.writeheader()
    dwriter.writerows(csv1)
