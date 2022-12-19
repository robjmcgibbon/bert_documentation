#!/usr/bin/env python3

"""
plot_sizes.py

Plot the file size as a function of snapshot index for FLAMINGO reduced snapshots.
This script can plot the output of the following du command:
 du -cs /cosma8/data/dp004/flamingo/Runs/L1000N1800/*/snapshots_reduces/f*
it is assumed the output is piped to a .txt file that is passed on
as argument to this script.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pl
import argparse
import re
import os

snapre = re.compile("flamingo_(\d+)\Z")


def get_index(filename):
    m = snapre.match(filename)
    if m is not None:
        return "snapshot", int(m.groups()[0])
    print(f'No match for filename "{filename}"')
    return None


argparser = argparse.ArgumentParser()
argparser.add_argument("input")
argparser.add_argument("output")
args = argparser.parse_args()

files = np.loadtxt(args.input, dtype=[("size", np.uint64), ("name", "U200")])

runs = {}
for file in files:
    path = file["name"].split("/")
    if len(path) < 3:
        print(f"Not a valid path: {file['name']}!")
        continue
    run_name = path[-3]
    if run_name not in runs:
        runs[run_name] = {}
    filename = path[-1]
    type, idx = get_index(filename)
    if type not in runs[run_name]:
        runs[run_name][type] = np.zeros(78, dtype=np.uint64)
    runs[run_name][type][idx] = file["size"]

fig, ax = pl.subplots(2, 1, sharex=True, figsize=(4, 8))

idx = np.arange(78)
for run in runs:
    if "DMO" in run:
        irow = 0
    else:
        irow = 1

    ax[irow].plot(idx, runs[run][type], label=run.replace("_", " "))

ax[0].set_title("reduced snapshots")

ax[0].set_ylabel("file size (kB)")
ax[1].set_ylabel("file size (kB)")
ax[1].set_xlabel("snap index")

ax[0].legend(loc="best")
ax[1].legend(loc="best")

pl.tight_layout()
pl.savefig(args.output, dpi=300)
