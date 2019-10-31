import csv

def get_csv(csvfile):
    csvdict = []
    with open(csvfile) as f:
        for item in csv.DictReader(f, skipinitialspace=True):
            csvdict.append(item)
    return csvdict

instances = get_csv('import-running.csv')
insttype=''
avgCPU=0
maxCPU=0
count = 0
for inst in instances:
    if insttype != inst['Type']:
        print(f'{insttype},{count},{avgCPU},{maxCPU}')
        insttype = inst['Type']
        avgCPU = float(inst['Avg'])
        maxCPU = float(inst['Max'])
        count = 1
    avgCPU = (avgCPU * count + float(inst['Avg'])) / (count +1)
    maxCPU = max(maxCPU, float(inst['Max']))
    count += 1
