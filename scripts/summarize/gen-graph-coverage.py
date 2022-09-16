#!/usr/bin/env python3

"""This script generates a scatterplot diagram of line coverage across sequences
   and experimental conditions."""

import argparse
import csv
import sys

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.ticker as tick


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile")
    parser.add_argument("--outfile", "-o", default="covplot.png")
    parser.add_argument("--covcolumn", "-t", choices = ["Application","Total"], default = "Application")
    return parser.parse_args()

def get_data(args, condition):
    x = []
    y = []
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if row["Condition"] != condition:
                continue
            x.append(row["Sequence"])
            y.append(int(row[args.covcolumn]))

    return (x,y)

args = get_args()
conditions = ["experimental", "control-customactionselection", "control-defaultactionselection"]
color_map = { "plain": "red", "experimental": "green", "control-customactionselection": "yellow", "control-defaultactionselection": "blue" }

fig, ax = plt.subplots()
ax.set_xlabel('Sequence number')
ax.set_ylabel('Line coverage')

for condition in conditions:
    (x,y) = get_data(args,condition)
    ax.scatter(x, y, c=color_map[condition], label=condition)

plt.legend(loc='lower right')
plt.savefig(args.outfile)
