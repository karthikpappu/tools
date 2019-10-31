import csv

def get_csv(csvfile):
    csvdict = []
    with open(csvfile) as f:
        for item in csv.DictReader(f, skipinitialspace=True):
            csvdict.append(item)
    return csvdict

def update_type(types,typename, minsize, maxsize):
    for itype in types:
        if typename == itype['Type']:
            itype['Min'] += minsize
            itype['Max'] += maxsize
            return types
    itype = {'Type':typename, 'Min': minsize, 'Max':maxsize}
    types.append(itype)

asgs = get_csv('asg.csv')
types = []
for asg in asgs:
    insttype = asg['Type']
    minsize = int(asg['Min'])
    maxsize = int(asg['Max'])
    update_type(types, insttype, minsize, maxsize)

print(types)
csvoutfile = 'asgsize.csv'
with open(csvoutfile, 'w') as outfile:
    dwriter = csv.DictWriter(outfile, types[0].keys())
    dwriter.writeheader()
    dwriter.writerows(types)
