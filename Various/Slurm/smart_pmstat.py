#!/usr/bin/env python3

"""
Wrapper around `pmstat`.

`pmstat` displays runtime information about a node or a set of nodes
(https://www.dur.ac.uk/icc/cosma/support/usage/pcp/)

Unfortunately, it needs a list of nodes as input, while it is usually more
convenient to provide a job ID. This script rectifies that.

Usage:
  ./smart_pmstat.py jobid [extra]
where jobid is the ID of a running job, and all other arguments are passed on
to `pmstat` as they are.
"""

import subprocess
import re
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("jobid")
argparser.add_argument("extra", nargs=argparse.REMAINDER)
args = argparser.parse_args()

# use `squeue` to find the node(s) this job is running on
cmd = f"squeue -j {args.jobid} -O NodeList:100"
df = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

stdout = df.stdout.decode("utf-8")
nodelist = stdout.split("\n")[1].strip()

# parse the node list into something that can be passed on to `pmstat`
nodes = []
if "[" in nodelist:
    for node in nodelist[2:-1].split(","):
        if "-" in node:
            begend = node.split("-")
            for i in range(int(begend[0]), int(begend[1]) + 1):
                nodes.append(i)
        else:
            nodes.append(int(node))
else:
    nodes = [nodelist[1:]]

# now run the `pmstat` command itself
pmstat_args = " ".join([f"-h m{node}" for node in nodes])
pmstat_extra = " ".join(args.extra)
cmd = f"pmstat {pmstat_args} {pmstat_extra}"
df = subprocess.run(cmd, shell=True)
