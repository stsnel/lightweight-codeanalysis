#!/usr/bin/env python3

"""This script generates a line graph that shows aggregate coverage
   for individual conditions, as well as combinations of the experimental
   condition with each control condition."""

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
    return parser.parse_args()

class LineData:
    def __init__(self):
        self.data=dict()

    def has_line(self, condition, filename, line):
        try:
            _ = self.data[condition][filename][line]
            return True
        except KeyError:
            return False

    def add(self, condition, filename, line):
        if condition not in self.data:
            self.data[condition] = dict()

        if filename not in self.data[condition]:
            self.data[condition][filename] = dict()

        if line not in self.data[condition][filename]:
            self.data[condition][filename][line] = 1


def get_cov_data(args):
    data = LineData()
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            data.add(row["Condition"], row["File"], row["Line"])
    return data

def get_cov_data_by_condition_seq(args, condition, sequence):
    data = []
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if ( row["Sequence"] == str(sequence) and
                 row["Condition"] == condition ):
                 data.append( (row["File"], row["Line"]) )
    return data

def get_plot_data(args, data, conditions):
    x = get_sequences(args)
    y = []
    for seq in x:
        linedata = set()
        for condition in conditions:
            linedata.update(set(get_cov_data_by_condition_seq(args, condition, seq)))
        y.append(len(linedata))
        print(f"Plot data for {str(conditions)} [{str(seq)}]: " + str(len(linedata)))
    return (x,y)


def get_conditions():
    return ["experimental", "control-defaultactionselection", "control-customactionselection"]

def get_sequences(args):
    max_sequence=1
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if int(row["Sequence"]) > max_sequence:
                max_sequence = int(row["Sequence"])

    return list(range(0, max_sequence + 1))

args = get_args()
data = get_cov_data(args)

color_map = { "experimental" : "red",
              "control-customactionselection" : "green",
              "control-defaultactionselection" : "blue"
            }
abbreviations = { "experimental" : "EXP", 
                  "control-customactionselection": "CCAS",
                  "control-defaultactionselection": "CDAS" }

fig, ax = plt.subplots()
ax.set_xlabel('Sequence number')
ax.set_ylabel('Aggregate line coverage')
plt.xticks(get_sequences(args))

# Single conditions
for condition in get_conditions():
    (x,y) = get_plot_data(args, data, [condition])
    color = color_map[condition]
    label = abbreviations[condition]
    ax.plot(x, y, c=color, label=label, linestyle = "solid")

# Experimental + other condition
for condition in get_conditions():
    if condition == "experimental":
        continue
    (x,y) = get_plot_data(args, data, ["experimental", condition])
    color = color_map[condition]
    label = abbreviations["experimental"] + " + " + abbreviations[condition]
    ax.plot(x, y, c=color, label=label, linestyle = "dotted")

plt.legend(loc='best')
plt.savefig(args.outfile)
