import argparse
import shutil
import datetime
import multiprocessing as mp

#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='multiprocessing rm a list of file/folders')
parser.add_argument('--targets-file', required=True)
parser.add_argument('-j', '--cores', type=int, default=2)
args = parser.parse_args()

def get_targets(targets_file):
    with open(targets_file) as f:
        dirs = f.readlines()
    dirs = [ x.strip() for x in dirs ]
    return dirs

def rmdir(dirname):
    with open('cleanup.log','a') as log:
        print('>>>', datetime.datetime.now(), dirname, file=log, flush=True)
    try:
        shutil.rmtree(dirname)
    except FileNotFoundError:
        pass
    with open('cleanup.log','a') as log:
        print('---', datetime.datetime.now(), dirname, file=log, flush=True)

dirs = get_targets(args.targets_file)

with mp.Pool(args.cores) as p:
    p.map(rmdir, dirs)
