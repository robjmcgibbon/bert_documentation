#!/usr/bin/env python3

"""
particle_lightcone_summary.py

Parse `lightcone_sizes.yml` (created with `particle_lightcone_sizes.py`) and
print its contents in human-friendly form.
"""

import yaml


def sizeof_fmt(num, suffix="B"):
    """
    Get the closest human-friendly size suffix for the given size in bytes.

    Shamelessly copy-pasted from Stackoverflow.
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Y", suffix)


with open("lightcone_sizes.yml", "r") as handle:
    data = yaml.safe_load(handle)

total = 0
for group in data:
    for dset in data[group]:
        total += data[group][dset]

for group in data:
    for dset in data[group]:
        size = data[group][dset]
        print(f"{group}/{dset}: {sizeof_fmt(size)} ({size/total*100.:.2f}%)")
