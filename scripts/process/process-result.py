#!/usr/bin/env python3

"""Prints CSV output with sequence result of each sequence (0 = OK, 1 = not OK)"""

import csv
from glob import glob
import os
import re
import sys

outputdir = "/data/studie/af/trial-run"
fieldnames = ["Experiment", "Condition", "Run", "Sequence", "Result"]
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
        for line in logfile:
            sequence = "?"
            result = "1"
            if bool(re.search(" Generate ", line)):
                for part in line.split(" "):
                    if part == "OK":
                        result="0"
                    elif part.endswith(".testar"):
                        filename = os.path.basename(part)
                        sequence = filename.split(".")[0].split("_")[-1]
                writer.writerow({ "Experiment" : exp,
                                  "Condition"  : condition,
                                  "Run"        : run,
                                  "Sequence"   : sequence,
                                  "Result"     : result })
