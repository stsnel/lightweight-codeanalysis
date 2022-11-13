#!/usr/bin/env python3

import argparse
import csv
import statistics
import sys

"""This script creates a table of the average coverage by
   sequence number and by condition"""

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile")
    parser.add_argument("--covcolumn", "-t", choices = ["Application","Total"], default = "Application")
    parser.add_argument("--aggregate", "-a", choices = ["mean","median"], default = "mean")
    parser.add_argument("--outformat", "-o", choices = ["csv","latex"], default = "csv")
    return parser.parse_args()


def get_central_coverage(args, condition, sequence):
    data = []
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if row["Condition"] == condition and row["Sequence"] == str(sequence):
                data.append(int(row[args.covcolumn]))

    if args.aggregate == "mean":
        return statistics.mean(data)
    elif args.aggregate == "median":
        return statistics.median(data)
    else:
        raise Exception("Unknown aggregation method: " + args.aggregate)

def get_sequences(args):
    max_sequence=1
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if int(row["Sequence"]) > max_sequence:
                max_sequence = int(row["Sequence"])

    return list(range(0,max_sequence + 1))

args = get_args()

conditions = { "experimental" : "Experimental",
               "control-defaultactionselection" : "Control (default AS)",
               "control-customactionselection"  : "Control (custom AS)" }

sequences = get_sequences(args)
results = []
for sequence in sequences:
    result = {}
    for condition, label in conditions.items():
        result[label] = str(round(get_central_coverage(args, condition, sequence)))
    result["Sequence"] = sequence
    results.append(result)

if args.outformat == "csv":
   fieldnames = ["Sequence", "Control (default AS)", "Control (custom AS)", "Experimental"]
   writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter = ';')
   writer.writeheader()
   for result in results:
       writer.writerow(result)
elif args.outformat == "latex":
   print("\\begin{center}")
   print("\\begin{tabular}{|l|l|l|l|}")
   print("\hline")
   print("Sequence number & Control (default AS) & Control (custom AS) & Experimental \\\\")
   print("\hline")
   for result in results:
       print( "{} & {} & {} & {} \\\\".format(
           result["Sequence"],
           result["Control (default AS)"],
           result["Control (custom AS)"],
           result["Experimental"]))
   print("\hline")
   print("\end{tabular}")
   print("\end{center}")
else:
    print("Error: unknown output format " + args.outformat)
    sys.exit(1)
