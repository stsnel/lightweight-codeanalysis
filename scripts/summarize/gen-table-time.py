#!/usr/bin/env python3

import argparse
import csv
import sys

import statistics

# This scripts compiles a table in CSV or LaTeX format of runtime / sequence time of the experiments

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile")
    parser.add_argument("--outformat", "-o", choices = ["csv","latex"], default = "csv")
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
results = []
for condition in conditions:
    data = get_data_by_condition(args, condition)
    avg = statistics.mean(data)
    sd = statistics.stdev(data)
    median = statistics.median(data)
    n = len(data)
    results.append( { "Condition": condition,
                      "Average": str(round(avg/1000,3)),
                      "Standard deviation": str(round(sd/1000,3)),
                      "Median": str(round(median/1000,3)),
                      "N": str(n) } )

if args.outformat == "csv":
   fieldnames = ["Condition", "Average", "Standard deviation", "Median", "N"]
   writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter = ';')
   writer.writeheader()
   for result in results:
       writer.writerow(result)
elif args.outformat == "latex":
   print("\\begin{center}")
   print("\\begin{tabular}{|l|l|l|l|l|}")
   print("\hline")
   print("Condition & Median & Average & Standard deviation & N \\\\")
   print("\hline")
   for result in results:
       print( "{} & {} & {} & {} & {} \\\\".format(
           result["Condition"],
           result["Median"],
           result["Average"],
           result["Standard deviation"],
           result["N"] ))
   print("\hline")
   print("\end{tabular}")
   print("\end{center}")
else:
    print("Error: unknown output format " + args.outoformat)
    sys.exit(1)

