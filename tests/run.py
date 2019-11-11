#!/usr/bin/env python

import os
import shutil
import subprocess
import sys
import glob

HERE = os.path.dirname(__file__)
POOLE = [
    os.path.join(HERE, "..", "env", "bin", sys.executable),
    os.path.join(HERE, "..", "poole.py"),
]
ACTUAL = os.path.join(HERE, "actual")
EXPECTED = os.path.join(HERE, "expected")
ERRORS = os.path.join(HERE, "errors.diff")

EX_OK = getattr(os, "EX_OK", 0)

if os.path.exists(ACTUAL):
    shutil.rmtree(ACTUAL)

if os.path.exists(ERRORS):
    os.remove(ERRORS)

cmd_init = POOLE + [ACTUAL, "--init"]
cmd_build_dry_run = POOLE + [ACTUAL, "--build", "--dry-run"]
cmd_build = POOLE + [ACTUAL, "--build"]
cmd_diff = ["diff", "-Naur", EXPECTED, ACTUAL]

r = subprocess.call(cmd_init, stdout=subprocess.PIPE)
if r != EX_OK:
    sys.exit(1)

r = subprocess.call(cmd_build_dry_run, stdout=subprocess.PIPE)
if r != EX_OK:
    sys.exit(1)

generated = glob.glob(os.path.join(ACTUAL, "output", "*"))
if generated != []:
    sys.exit(1)

r = subprocess.call(cmd_build, stdout=subprocess.PIPE)
if r != EX_OK:
    sys.exit(1)

generated = glob.glob(os.path.join(ACTUAL, "output", "*"))
if generated == []:
    sys.exit(1)

p = subprocess.Popen(cmd_diff, stdout=subprocess.PIPE)
diff = p.communicate()[0]
if diff:
    with open(ERRORS, 'wb') as fp:
        fp.write(diff)
    print("failed - see %s for details" % ERRORS)
    sys.exit(1)

print("passed")
