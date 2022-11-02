#!/usr/bin/env python3

"""Prints CSV file with total and application coverage per experiment/condition/run/sequence"""

import csv
from glob import glob
import os
import re
import sys

import sqlite3

# This function was copied from CoveragePy, Apache2 license
def numbits_to_nums(numbits):
    """Convert a numbits into a list of numbers.
    Arguments:
        numbits: a binary blob, the packed number set.
    Returns:
        A list of ints.
    When registered as a SQLite function by :func:`register_sqlite_functions`,
    this returns a string, a JSON-encoded list of ints.
    """
    nums = []
    for byte_i, byte in enumerate(numbits):
        for bit_i in range(8):
            if (byte & (1 << bit_i)):
                nums.append(byte_i * 8 + bit_i)
    return nums


outputdir = "/data/studie/af/trial-run"
fieldnames = ["Experiment", "Condition", "Run", "Sequence", "Total", "Application", ]
writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter = ';')
writer.writeheader()

for dir in glob(f"{outputdir}/*"):
    if not os.path.isdir(dir):
        continue
    basename = os.path.basename(dir)
    basename_parts = basename.split(".")

    if len(basename_parts) != 3:
        print(f"Dir {basename} is not in expected three part format. Skipping.")
        continue

    (exp,condition,run) = basename_parts

    for coverage_file in glob(f"{dir}/coverage-*.dump"):
        coverage_file_basename = os.path.basename(coverage_file)
        sequence_number = coverage_file_basename.split("-")[1]
        os_lines = 0
        app_lines = 0
        if os.path.isfile("tmp.db"):
            os.remove("tmp.db")
        os.system(f'bash -c "sqlite3 tmp.db < {coverage_file}"')
        connection = sqlite3.connect("tmp.db")
        cur = connection.cursor()
        bits = cur.execute("select file.path, line_bits.numbits from file join line_bits on file.id = line_bits.file_id;")
        for data in bits.fetchall():
            (filename,bits) = data
            num_lines = len(numbits_to_nums(bits))
            if filename.startswith("/usr/lib/ckan/venv/src/ckan") or filename.startswith("/opt/indico/src/indico/"):
                app_lines += num_lines
            elif filename.startswith("/usr/lib/python3."):
                os_lines += num_lines
            else:
                print("Warning lines in file of unknown type " + filename + " ignored.")
        writer.writerow( { "Experiment" : exp,
                           "Condition" : condition,
                           "Run" : run,
                           "Sequence" : sequence_number,
                           "Total" : app_lines + os_lines,
                           "Application" : app_lines } )
