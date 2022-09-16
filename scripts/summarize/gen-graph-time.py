#!/usr/bin/env python3

import argparse
import csv
import sys

import numpy as np
from matplotlib import pyplot as plt

# This scripts compiles a table in CSV or LaTeX format of runtime / sequence time of the experiments

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile")
    parser.add_argument("--outfile", "-o", default="plot.png")
    parser.add_argument("--timecolumn", "-t", choices = ["Time","Runtime"], default = "Runtime")
    return parser.parse_args()

def get_data_by_condition(args, condition):
    data = []
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if row["Condition"] == condition:
                data.append(int(row[args.timecolumn]))
    return data

args = get_args()
conditions = ["plain", "experimental", "control-customactionselection", "control-defaultactionselection"]
tot_data = []

for condition in conditions:
    data = get_data_by_condition(args, condition)
    n = len(data)
    tot_data.append(np.array(data))

fig = plt.figure(figsize =(10, 7))
 
ax = fig.add_axes([0, 0, 1, 1])

# x-axis labels
#ax.set_xticklabels(conditions)
 
bp = ax.boxplot(tot_data, labels=conditions)
 
plt.savefig(args.outfile)
