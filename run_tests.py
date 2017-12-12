#!/usr/bin/python3

import os
import re
import sys
import subprocess
from argparse import ArgumentParser
from sys import platform as _platform

class bcolors:
    SUCCESS = '\033[32m'
    WARNING = '\033[33m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'

def myprint(color, s, *args):
  if _platform != "win32" and sys.stdout.isatty():
    print(color, s, bcolors.ENDC, *args)
  else:
    print(*args)

parser = ArgumentParser()
parser.add_argument("--max-iters", dest="max_iters", type=int, \
                                help="Limit number of iterations", default=15)
parser.add_argument("--solver", dest="solver", action="store", \
                                help="Choose SMT solver", default="z3")
parser.add_argument(dest="folder", action="store", help="Select test folder")

options = parser.parse_args()

if options.folder == "" or not os.path.exists(options.folder):
    parser.error("Please supply directory of tests")
    sys.exit(1)
    
test_dir = os.path.abspath(options.folder)

if not os.path.isdir(test_dir):
    print("Please provide a directory of test scripts.")
    sys.exit(1)

files = [ f for f in os.listdir(test_dir) if re.search(".py$",f) ]

failed = []
for f in files:
    # execute the python runner for this test
        full = os.path.join(test_dir, f)
        with open(os.devnull, 'w') as devnull:
            ret = subprocess.call([sys.executable, "PyExSMT.py", \
                            "--max-iters", str(options.max_iters), "--solver", options.solver \
                            , full], stdout=devnull)
        if (ret == 0):
            myprint(bcolors.SUCCESS, "✓", "Test " + f + " passed.")
        else:
            failed.append(f)
            myprint(bcolors.FAIL, "✗", "Test " + f + " failed.")

if failed != []:
    print("RUN FAILED")
    print(failed)
    sys.exit(1)
else:
    sys.exit(0)
