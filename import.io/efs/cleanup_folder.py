import os, shutil
import argparse

#
# Command Line Arguments
#
parser = argparse.ArgumentParser(description='clean up folders')
parser.add_argument('--rootdir', default='.')
parser.add_argument('--expiration', type=int)
parser.add_argument('--dryrun', action='store_true')
args = parser.parse_args()

#
print(args.expiration)
