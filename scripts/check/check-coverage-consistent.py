#!/usr/bin/env python3

# Checks that coverage data is consistent with raw coverage
# data, in the sense that coverage in individual runs should
# never exceed aggregated raw coverage across all runs.

import argparse
import csv

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("covfile")
    parser.add_argument("rawcovfile")
    return parser.parse_args()

def get_condition_sequence_pairs(args):
    result = set()
    with open(args.rawcovfile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            result.add( (row["Condition"], row["Sequence"]) )

    return result

def get_rawcoverage(args, condition, sequence):
    lines = set()

    with open(args.rawcovfile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if row["Condition"] == condition and row["Sequence"] == str(sequence):
                lines.add( (row["File"], row["Line"]) )

    return len(lines)

args = get_args()
for (condition, sequence) in get_condition_sequence_pairs(args):
    raw_coverage = get_rawcoverage(args, condition, sequence)
    with open(args.covfile, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter =';')
        for row in reader:
            if row["Condition"] == condition and row["Sequence"] == str(sequence):
                total_coverage = int(row["Total"])
                run = row["Run"]
                if total_coverage > raw_coverage:
                    print(f"Warning: total coverage for {condition}/{run}/{sequence} is too high: " +
                          f"{total_coverage} > {raw_coverage}")
                else:
                    print(f"OK: {condition}/{run}/{sequence} seems okay: " +
                          f"{total_coverage} =< {raw_coverage}")
