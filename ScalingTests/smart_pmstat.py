#!/usr/bin/env python3

"""
Smart wrapper around pmstat
Usage:
  smart-pmstat JOBID [ADDITIONAL ARGUMENTS]

Where JOBID is the SLURM id of a running job.
The script will first recover the corresponding nodes using `squeue`, and will
then start a continuous monitoring of the corresponding nodes with `pmstat`.
Additional arguments are passed on directly to `pmstat`.

Since `pmstat` does not exit until it is interrupted, the same is true for
this script.
"""

import subprocess
import re
import argparse

# parse command line arguments
argparser = argparse.ArgumentParser()
argparser.add_argument("jobid")
argparser.add_argument("extra", nargs=argparse.REMAINDER)
args = argparser.parse_args()

# get the nodelist from `squeue`
cmd = f"squeue -j {args.jobid} -O NodeList:100"
df = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

stdout = df.stdout.decode("utf-8")
nodelist = stdout.split("\n")[1].strip()

nodes = []
if "[" in nodelist:
    # split into the individual nodes
    # nodes are generally listed as e.g. m[8202,8342,8349-8350]
    for node in nodelist[2:-1].split(","):
        if "-" in node:
            begend = node.split("-")
            for i in range(int(begend[0]), int(begend[1]) + 1):
                nodes.append(i)
        else:
            nodes.append(int(node))
else:
    # there is only one node
    nodes = [nodelist[1:]]

# run `pmstat` on the nodes
pmstat_args = " ".join([f"-h m{node}" for node in nodes])
pmstat_extra = " ".join(args.extra)
cmd = f"pmstat {pmstat_args} {pmstat_extra}"
df = subprocess.run(cmd, shell=True)
