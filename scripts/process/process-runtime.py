#!/usr/bin/env python3

"""Prints CSV output with time of each experiment run in milliseconds"""

import csv
from glob import glob
import os
import re
import sys

outputdir = "/data/studie/af/trial-run"
fieldnames = ["Experiment", "Condition", "Run", "Runtime"]
writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter = ';')
writer.writeheader()

for dir in glob(f"{outputdir}/*"):
    if not os.path.isdir(dir):
        continue
    basename = os.path.basename(dir)
    basename_parts = basename.split(".")

    if len(basename_parts) != 3:
        print(f"Dir {basename} is not in expected three part format. Skipping.")
        continue

    (exp,condition,run) = basename_parts

    with open(f"{dir}/experiment.log") as logfile:
        begin_ts = -1
        end_ts = -1

        for line in logfile:
            if re.search("Begin experiment \(TS\) \@ ", line):
                begin_ts = int(line.split(" ")[-1])
            elif re.search("End experiment \(TS\) \@ ", line):
                end_ts = int(line.split(" ")[-1])

        if begin_ts == -1 or end_ts == -1:
            time="?"
        else:
            time=str(end_ts-begin_ts)

    writer.writerow({ "Experiment"  : exp,
                      "Condition"   : condition,
                      "Run"         : run,
                      "Runtime"     : time})
