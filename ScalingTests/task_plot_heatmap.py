#!/usr/bin/env python3

"""
Create a thread heat map from a task plot file for a single step (no-MPI only).
Usage:
  ./task_plot_heatmap TASKFILE OUTPUTFILE
where TASKFILE is the name of a valid SWIFT task plot output file, and
OUTPUTFILE is the name of an image file that will be created.

This script reads in the task plot file and maps all tasks onto a 2D activity
histogram, i.e. an anonymous version of the usual task plot.
The histogram is then sorted in the vertical direction, creating a heatmap of
how much activity there was over time.
The histogram is also used to visualise the average thread activity and the
total efficiency as a function of time.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pl
import argparse

# parse command line arguments
argparser = argparse.ArgumentParser("Analyze the load balance in a task plot file.")
argparser.add_argument("tasks", help="Input task plot file")
argparser.add_argument("output", help="Name of the output file")
args = argparser.parse_args()

# fixed size for the histogram. This value works well.
map_size = 10000

# load the task plot data (only the columns we need)
sdata = np.loadtxt(
    args.tasks,
    usecols=(0, 1, 2, 4, 5),
    dtype=[
        ("thread", "i4"),
        ("task", "i4"),
        ("subtask", "i4"),
        ("tic", "i8"),
        ("toc", "i8"),
    ],
)

# filter out lines containing metadata
sdata = sdata[sdata["thread"] >= 0]
# get the number of threads
nthread = len(np.unique(sdata["thread"]))
# get the task time range and use to compute a factor that can be used to
# convert tic into an offset in the histogram
mintic = sdata["tic"].min()
maxtoc = sdata["toc"].max()
fac = map_size / (maxtoc - mintic)

# create the empty task histogram
task_map = np.zeros((nthread, map_size), dtype=bool)

# loop over tasks
for task in sdata:
    # compute the offset and size of the task in the task histogram
    thread = task["thread"]
    beg = int(np.round(fac * (task["tic"] - mintic)))
    # commented out line: force each task to be at least one column wide
    # end = max(beg+1,int(np.round(fac * (task["toc"] - mintic))))
    end = int(np.round(fac * (task["toc"] - mintic)))
    # activate this region in the histogram
    task_map[thread, beg:end] = True

# compute global statistics: the average load per thread
nactive = task_map.sum()
ntotal = nthread * map_size
print(f"Average load per thread: {nactive / ntotal}")

# compute per thread load statistics
nactive = task_map.sum(axis=1)
ntotal = map_size
print(f"Load per thread: {nactive / ntotal}")

# output figure
pl.rcParams["figure.figsize"] = (12, 8)

ax = [
    pl.subplot2grid((3, 2), (0, 0), colspan=2),
    pl.subplot2grid((3, 2), (1, 0), colspan=2),
    pl.subplot2grid((3, 2), (2, 0)),
    pl.subplot2grid((3, 2), (2, 1)),
]

ax[0].set_title("original task plot")
ax[0].imshow(task_map, aspect="auto")

ax[1].set_title("sorted vertically (heat map)")
task_map = np.sort(task_map, axis=0)
ax[1].imshow(task_map, aspect="auto")

ax[2].set_title("thread efficiency")
ax[2].semilogy(np.arange(map_size), task_map.sum(axis=0) / nthread)
ax[2].set_xticks([])
ax[2].set_ylabel("fraction of threads active")
ax[2].set_xlabel("step fraction")

ax[3].set_title("thread load")
ax[3].bar(np.arange(nthread), nactive / ntotal, width=1.0)
ax[3].set_ylim(0.0, 1.0)
ax[3].set_ylabel("fraction of time active")
ax[3].set_xlabel("thread number")

ax[0].axis("off")
ax[1].axis("off")

pl.tight_layout()
pl.savefig(args.output, dpi=300)
