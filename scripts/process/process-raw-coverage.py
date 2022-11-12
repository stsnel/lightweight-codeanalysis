#!/usr/bin/env python3

"""Prints CSV file with covered files and lines per experiment/condition/run/sequence"""

import csv
from glob import glob
import os
import re
import sys

from nested_dict import nested_dict

import sqlite3

class UniqueLineCache:
    def __init__(self):
        self.line_cache=dict()

    def check_seen(self, condition, sequence, filename, line):
        try:
            _ = self.line_cache[condition][sequence][filename][line]
            return True
        except KeyError:
            self._update(condition, sequence, filename, line)
            return False

    def _update(self, condition, sequence, filename, line):
        if condition not in self.line_cache:
            self.line_cache[condition] = dict()

        if sequence not in self.line_cache[condition]:
            self.line_cache[condition][sequence] = dict()

        if filename not in self.line_cache[condition][sequence]:
            self.line_cache[condition][sequence][filename] = dict()

        if line not in self.line_cache[condition][sequence][filename]:
            self.line_cache[condition][sequence][filename][line] = 1
            

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


cache = UniqueLineCache()
outputdir = "/data/studie/af/output-1509"
fieldnames = ["Condition", "Sequence", "File", "Line", ]
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
            filename = filename.replace("/./","/")
            for line in numbits_to_nums(bits):
                if not cache.check_seen(condition, sequence_number, filename, line):
                    writer.writerow( { "Condition" : condition,
                                       "Sequence" : sequence_number,
                                       "File" : filename,
                                       "Line" : line } )
