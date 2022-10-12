#!/usr/bin/env python3

"""This script generates a differential coverage table based on
   raw coverage CSV file. It shows how many lines were covered by
   a condition that were not covered by another condition."""

import argparse
import csv
import sys

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile")
    parser.add_argument("--outformat", "-o", choices = ["csv","latex"], default = "csv")
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

def get_cov_data_by_condition(args, condition):
    data = []
    seen_before = dict()
    with open(args.infile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if row["Condition"] == condition:
                f = row["File"]
                l = row["Line"]
                key = f"{f}:{l}"
                if key not in seen_before:
                    data.append( (row["File"], row["Line"]) )
                seen_before[row["File"] + ":" + row["Line"]] = 1
    return data

def get_comparison_data(args, data):
    result = dict()
    for condition_a in get_conditions():
        result[condition_a] = dict()
        base_data = get_cov_data_by_condition(args, condition_a)
        for condition_b in get_conditions():
            only_base_count = 0
            for (file, line) in base_data:
                if not data.has_line(condition_b, file, line):
                    only_base_count+=1
            result[condition_a][condition_b] = only_base_count
    return result

def get_conditions():
    return ["experimental", "control-defaultactionselection", "control-customactionselection"]

args = get_args()
data = get_cov_data(args)
comparison_data = get_comparison_data(args, data)

if args.outformat == "csv":
   fieldnames = ["Condition", "Not in experimental", "Not in control (default AS)", "Not in control (custom AS)"]
   writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter = ';')
   writer.writeheader()
   for condition in get_conditions():
       writer.writerow({"Condition": condition,
                        "Not in experimental": comparison_data[condition]["experimental"],
                        "Not in control (default AS)": comparison_data[condition]["control-defaultactionselection"],
                        "Not in control (custom AS)": comparison_data[condition]["control-customactionselection"]})
elif args.outformat == "latex":
   print("\\begin{center}")
   print("\\begin{tabular}{|l|l|l|l|}")
   print("\hline")
   print("Condition & Not in experimental & Not in control & Not in control\\\\")
   print("          &                     & (default AS)   & (custom AS)\\\\")
   print("\hline")
   for condition in get_conditions():
       print( "{} & {} & {} & {} \\\\".format(
           condition,
           comparison_data[condition]["experimental"],
           comparison_data[condition]["control-defaultactionselection"],
           comparison_data[condition]["control-customactionselection"] ))
   print("\hline")
   print("\end{tabular}")
   print("\end{center}")
else:
    print("Error: unknown output format " + args.outformat)
