#!/usr/bin/env python3

"""This script generates a graph of the average line coverage by
   condition and sequence"""

import argparse
import csv

from matplotlib import pyplot as plt

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile")
    parser.add_argument("--outfile", "-o", default="covseqplot.png")
    return parser.parse_args()

def get_cov_data(args, condition):
    data = []
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            data.append(int(row[condition]))

    return data


args = get_args()
condition_colors = { "Experimental": "red",
                     "Control (default AS)" : "blue",
                     "Control (custom AS)": "green" }

sequences = list(range(0, 10))

for condition, color in condition_colors.items():
    plt.plot(sequences, get_cov_data(args, condition), color=color, label=condition)

plt.title('Coverage by condition and sequence')
plt.xlabel('Sequence')
plt.ylabel('Coverage')
plt.grid(True)
plt.legend(loc='lower right')
plt.savefig(args.outfile)
