#!/usr/bin/env python3

"""
check_snapshots.py

Check that all FLAMINGO L1000N1800/{runs}/snapshots files are on tape and on
disk, by running a `find` command ({runs} is the list provided below).
Each run is parsed separately on disk and on tape, and the output for every
`find` command is stored in a separate `.txt` file, `<RES>_<RUN>_<MEDIUM>.txt`,
where `RES=L1000N1800`, `RUN={run}` and `MEDIUM=disk/tape`.
"""

import subprocess
import time


def run_cmd(cmd):
    """
    Use subprocess to run `cmd`. Time the command duration and check its return
    code.
    """
    print(f"Running {cmd}...")
    tic = time.time()
    handle = subprocess.run(cmd, shell=True)
    if handle.returncode != 0:
        raise RuntimeError(f"Command {cmd} did not succeed!")
    toc = time.time()
    print(f"Done, took {toc-tic:.2f} s.")


basefolder = "/cosma8/data/dp004/flamingo/Runs"
resfolder = "L1000N1800"
runs = [
    "DMO_FIDUCIAL",
    "DMO_PLANCK",
    "DMO_PLANCK_LARGE_NU_FIXED",
    "DMO_PLANCK_LARGE_NU_VARY",
    "DMO_PLANCK_MID_NU_VARY",
    "HYDRO_FIDUCIAL",
    "HYDRO_PLANCK",
    "HYDRO_PLANCK_LARGE_NU_FIXED",
    "HYDRO_PLANCK_LARGE_NU_VARY",
    "HYDRO_STRONG_AGN",
    "HYDRO_WEAK_AGN",
]

for run in runs:
    path = f"{basefolder}/{resfolder}/{run}/snapshots"
    outfile = f"{resfolder}_{run}"
    tapecmd = f"tape.py find {path} | tee {outfile}_tape.txt"
    diskcmd = f"find {path} | tee {outfile}_disk.txt"
    run_cmd(tapecmd)
    run_cmd(diskcmd)
