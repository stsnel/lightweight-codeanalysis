#!/usr/bin/env python3

"""This scripts generated a bar graph of the average time per
   action across conditions."""

import argparse
import csv
import matplotlib.pyplot as plt

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile")
    parser.add_argument("--outfile", "-o", default="actiontimeplot.png")
    return parser.parse_args()

def get_average_actiontime(args, condition):
    x = []
    y = []
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if row["Condition"] == condition:
                return float(row["Average"])


args = get_args()

fig, ax = plt.subplots()

ax = fig.add_axes([0,0,1,1])
ax.set_xlabel('Condition')
ax.set_ylabel('Average time per action (sec)\nincluding instrumentation calls')
ax.legend("Conditions")

conditions = ["plain", "control-defaultactionselection", "control-customactionselection", "experimental"]
condition_labels = ["control (plain)", "control (default AS)", "control (custom AS)", "experimental"]
condition_values = [ get_average_actiontime(args, condition) for condition in conditions ]
condition_colors = ["yellow", "green", "blue", "red"]
condition_ticks = [0,1,2,3]

ax.bar(condition_ticks, condition_values, color=condition_colors)
ax.set_xticks(condition_ticks)
ax.set_xticklabels(condition_labels)
plt.savefig(args.outfile, bbox_inches='tight')
