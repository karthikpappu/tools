# Import the os module, for the os.walk function
import os
import os.path
import sys
import argparse
import time

#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='Find Last modification and access time')
parser.add_argument('--rootdir', default='.')
parser.add_argument('--save-to')
parser.add_argument('--dryrun', action='store_true')
args = parser.parse_args()

#
# Results
#

#within = {1: '1d', 7: '1w', 14: '2w', 30: '1m', 60: '2m', 90: '3m', 182: '6m', 365: '1y', 730: '2y', 3650: '10y', 36500: 'error'}
within = {7: 'Now', 14: '1 week old', 30: '2 weeks old', 36500: '1 month old'}

mcount = {}
acount = {}
msize = {}
asize = {}

def init():
    for key in within:
        mcount.update({key: 0})
        acount.update({key: 0})
        msize.update({key: 0})
        asize.update({key: 0})

def days_to_now(ts):
    return (time.time() - ts) / (24 * 60 * 60)

def daysgroup(ts):
    days = days_to_now(ts)
    dgroup = 36500
    for d in within:
        if days <= d:
            dgroup = min(dgroup, d)

    return dgroup

def print_result(mcount, acount, msize, asize, save_to=None):
    print('Age Group,Count by Modified,Count By Access,Size By Modified,Size By Access', file=save_to)
    for age in within:
        print(f'{within[age]},{mcount[age]},{acount[age]},{msize[age]},{asize[age]}', file=save_to)

init()

# Set the directory you want to start from
rootdir = os.path.abspath(args.rootdir)
count = 0
for dirName, subdirList, fileList in os.walk(rootdir):
    for fname in fileList:
        fpath = dirName+'/'+fname
        if os.path.isfile(fpath):
            stinfo = os.stat(fpath)
            adays = daysgroup(stinfo.st_atime)
            mdays = daysgroup(stinfo.st_mtime)
            size = stinfo.st_size
            #print(os.path.getatime(fpath), os.path.getmtime(fpath), fpath)
            #print("\n",fpath)
            mcount[mdays] += 1
            acount[adays] += 1
            msize[mdays] += size
            asize[adays] += size
            count += 1
        if count % 1000000 == 0:
            print(f'\n\t{count} files Result')
            print_result(mcount, acount, msize, asize)

if args.save_to is not None:
    save_to = open(args.save_to, 'w')
else:
    print("\n\tFinal Result")
    save_to = None

print_result(mcount, acount, msize, asize, save_to=save_to)

if args.save_to is not None:
    save_to.close()
    print(f"Saved to {args.save_to}")
