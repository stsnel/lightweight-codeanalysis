#!/usr/bin/env python3

"""This script generates a differential coverage scatterplot based on
   raw coverage CSV file. It shows how many lines were covered by
   a condition that were not covered by another condition."""

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

def get_cov_data_by_condition_and_seq(args, condition, sequence = None):
    data = []
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if ( row["Condition"] == condition and 
                 (sequence is None or row["Sequence"] == str(sequence)) ):
                data.append( (row["File"], row["Line"]) )
    return data

def get_comparison_data(args, data):
    result = dict()
    sequences = get_sequences()
    for condition_a in get_conditions():
        result[condition_a] = dict()
        for condition_b in get_conditions():
            result[condition_a][condition_b] = dict()
        for seq in sequences:
            result
            base_data = get_cov_data_by_condition_and_seq(args, condition_a, seq)
            for condition_b in get_conditions():
                only_base_count = 0
                for (file, line) in base_data:
                    if not data.has_line(condition_b, file, line):
                        only_base_count+=1
                result[condition_a][condition_b][str(seq)] = only_base_count
    return result

def get_plot_data(comparison_data, condition_a, condition_b):
    x = get_sequences()
    y = []
    for seq in get_sequences():
        y.append(comparison_data[condition_a][condition_b][str(seq)])
    return (x,y)

def get_conditions():
    return ["experimental", "control-defaultactionselection", "control-customactionselection"]

def get_sequences():
    return list(range(5))

args = get_args()
data = get_cov_data(args)
comparison_data = get_comparison_data(args, data)

color_map = { "experimental" : { "control-customactionselection": "lightgreen", "control-defaultactionselection": "darkgreen" },
              "control-customactionselection" : { "experimental": "lightblue", "control-defaultactionselection": "darkblue" },
              "control-defaultactionselection" : { "experimental": "red", "control-customactionselection": "darkred" }
            }
abbreviations = { "experimental" : "EXP", "control-customactionselection": "CCAS", "control-defaultactionselection": "CDAS" }

fig, ax = plt.subplots()
ax.set_xlabel('Sequence number')
ax.set_ylabel('Diff line coverage')
plt.xticks(get_sequences())

for condition_a in get_conditions():
    for condition_b in get_conditions():

        if condition_a == condition_b:
            continue

        (x,y) = get_plot_data(comparison_data, condition_a, condition_b)
        color = color_map[condition_a][condition_b]
        label = label="{} over {}".format(abbreviations[condition_a], abbreviations[condition_b])
        ax.scatter(x, y, c=color, label=label)

plt.legend(loc='upper left')
plt.savefig(args.outfile)
