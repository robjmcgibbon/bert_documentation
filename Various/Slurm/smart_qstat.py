#!/usr/bin/env python3

"""
Wrapper around `squeue` that displays some more user-friendly information.

Information is ordered in a more visually pleasing way, and some bits of
information are displayed in a way that is more useful than the default.
Job names for example can be up to 100 characters long, instead of the default,
which is only 8.

A subset of the `squeue` arguments are supported, sometimes with a different
name:
 --wdir/-w:   show the working directory for a job (directory from which the job
              was submitted)
 --submit/-s: show the time a job was submitted
 --start/-S:  show the time a job actually started
 --cpus/-c:   show on how many CPUs the job is running
 --user/-u:   only show jobs for the given user (default: dc-vand2)
 --queue/-p:  only show jobs submitted to the given queue
 --array/-a:  show additional information for array jobs, i.e the parent job
              ID (needed to cancel or edit the whole array) and the index in
              the array of the particular job (useful for distinguishing
              different jobs in the same array).

As an added bonus, we use ASCII colour codes to make the output somewhat more
visually appealing.
"""

import subprocess
import re
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--wdir", "-w", action="store_true")
argparser.add_argument("--submit", "-s", action="store_true")
argparser.add_argument("--start", "-S", action="store_true")
argparser.add_argument("--cpus", "-c", action="store_true")
argparser.add_argument("--user", "-u", default="dc-vand2")
argparser.add_argument("--queue", "-p", default=None)
argparser.add_argument("--array", "-a", action="store_true")
args = argparser.parse_args()

cmd = "squeue"
if not args.queue is None:
    cmd += " -p {0}".format(args.queue)
else:
    cmd += " -u {0}".format(args.user)
cmd += " -O JobID,MaxCPUs,MaxNodes,Name:100,State,StartTime,SubmitTime,TimeLeft,WorkDir:200,ArrayJobID,ArrayTaskID"
df = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

fmt = "{0:8} {1:8} {2:>5} {3:>9}"
if args.cpus:
    fmt += "{8:>6}"
fmt += "  {4}"
if args.wdir:
    fmt += "\n{5}"
if args.submit:
    fmt += "\nSubmitted on {6}"
if args.start:
    fmt += "\nStart on {7}"
if args.array:
    fmt += "\nArray: {9} [{10}]"
print(
    fmt.format(
        "JobID",
        "State",
        "Nodes",
        "TimeLeft",
        "Name",
        "Working directory",
        "Submit time",
        "Start time",
        "Cores",
        "ArrayJobID",
        "ArrayTaskID",
    )
)
for line in df.stdout.decode("utf-8").split("\n")[1:]:
    data = line.split()
    if len(data) > 0:
        if data[4] == "RUNNING":
            print(
                "\u001b[32m"
                + fmt.format(
                    data[0],
                    data[4],
                    data[2],
                    data[7],
                    data[3],
                    data[8],
                    data[6],
                    data[5],
                    data[1],
                    data[9],
                    data[10],
                )
                + "\u001b[0m"
            )
        else:
            print(
                "\u001b[36m"
                + fmt.format(
                    data[0],
                    data[4],
                    data[2],
                    data[7],
                    data[3],
                    data[8],
                    data[6],
                    data[5],
                    data[1],
                    data[9],
                    data[10],
                )
                + "\u001b[0m"
            )
