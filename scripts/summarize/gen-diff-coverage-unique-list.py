#!/usr/bin/env python3

"""This script generates a differential coverage CSV file based on
   raw coverage CSV file. It shows each line that was covered
   by one condition, but not by either other one."""

import argparse
import csv
import sys

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile")
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

def get_diff_lines(args, data, condition_a, other_conditions):
    result = []

    for (filename, line) in get_cov_data_by_condition(args, condition_a):
        in_other_condition = False
        for other_condition in other_conditions:
            if data.has_line(other_condition, filename, line):
                in_other_condition = True
        if not in_other_condition:    
            result.append( (filename, line) )

    return result


def get_conditions():
    return ["experimental", "control-defaultactionselection", "control-customactionselection"]

def get_other_conditions(condition):
    conditions = get_conditions()
    conditions.remove(condition)
    return conditions

args = get_args()
data = get_cov_data(args)

fieldnames = ["Condition", "File", "Line number"]
writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter = ';')
writer.writeheader()
for condition in get_conditions():
    for (filename, line) in get_diff_lines(args, data, condition, get_other_conditions(condition)):
        writer.writerow({ "Condition": condition,
                          "File": filename,
                          "Line number": line })
