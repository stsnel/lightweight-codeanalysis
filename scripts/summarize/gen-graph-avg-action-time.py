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

conditions = ["experimental", "control-defaultactionselection", "control-customactionselection", "plain"]
condition_labels = ["experimental", "control (default AS)", "control (custom AS)", "control (plain)"]
condition_values = [ get_average_actiontime(args, condition) for condition in conditions ]
condition_colors = ["red", "green", "blue", "yellow"]

ax.bar(condition_labels, condition_values, color=condition_colors)
plt.savefig(args.outfile, bbox_inches='tight')
