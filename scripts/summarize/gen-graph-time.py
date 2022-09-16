#!/usr/bin/env python3

"""This script generates a boxplot of sequence or run times across
   experimental conditions."""

import argparse
import csv
import sys

import numpy as np
from matplotlib import pyplot as plt

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
                data.append(int(row[args.timecolumn])/1000)
    return data

args = get_args()
conditions = ["plain", "experimental", "control-customactionselection", "control-defaultactionselection"]
condition_labels = ["plain", "experimental", "control\n(custom AS)", "control\n(default AS)"]
tot_data = []

for condition in conditions:
    data = get_data_by_condition(args, condition)
    n = len(data)
    tot_data.append(np.array(data))

fig, ax = plt.subplots()
 
ax.set_xticklabels(conditions)
ax.set_xlabel('Condition')
ax.set_ylabel('Time in seconds')
 
bp = ax.boxplot(tot_data, labels=condition_labels)
 
plt.tight_layout()
plt.savefig(args.outfile)
