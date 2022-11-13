#!/usr/bin/env python3

""" Creates a histogram of line coverage for each sequence, by condition."""

import argparse
import csv
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.ticker as tick


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile")
    parser.add_argument("--outfile", "-o", default="covhistogram.png")
    parser.add_argument("--covcolumn", "-t", choices = ["Application","Total"], default = "Application")
    return parser.parse_args()

def get_coverage_list_by_condition(args, condition):
    results = []
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if row["Condition"] == condition:
                results.append(int(row[args.covcolumn]))

    return results


conditions = ["experimental", "control-defaultactionselection", "control-customactionselection"]
colormap = { "experimental": "red",
             "control-defaultactionselection": "blue",
             "control-customactionselection": "green" }
labelmap = { "experimental": "Experimental",
             "control-defaultactionselection": "Control (default AS)",
             "control-customactionselection": "Control (custom AS)" }
args = get_args()

for condition in conditions:
    data = get_coverage_list_by_condition(args, condition)
    _, _, _ = plt.hist(data, bins=50, color=colormap[condition], label=labelmap[condition], alpha=0.8)

plt.legend(loc='best')
plt.xlabel('Line coverage per sequence')
plt.ylabel('N')
plt.savefig(args.outfile)
