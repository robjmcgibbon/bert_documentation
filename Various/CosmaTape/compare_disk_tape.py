#!/usr/bin/env python3

"""
compare_disk_tape.py

Takes the output of the other script in this directory and does a one to one
comparison. Since the full path on tape and disk is not necessarily the same,
this script only compares the final part of the path, e.g. the snapshot folder
and the individual snapshot files.
"""

import numpy as np

sim = "L1000N1800"
runs = [
    "DMO_FIDUCIAL",
    "DMO_PLANCK",
    "DMO_PLANCK_LARGE_NU_FIXED",
    "DMO_PLANCK_LARGE_NU_VARY",
    "HYDRO_FIDUCIAL",
    "HYDRO_PLANCK",
    "HYDRO_PLANCK_LARGE_NU_FIXED",
    "HYDRO_PLANCK_LARGE_NU_VARY",
    "HYDRO_STRONG_AGN",
    "HYDRO_WEAK_AGN",
]

for run in runs:
    diskfile = f"{sim}_{run}_disk.txt"
    tapefile = f"{sim}_{run}_tape.txt"
    files = {}
    for name, file in {"disk": diskfile, "tape": tapefile}.items():
        with open(file, "r") as handle:
            this_files = []
            for line in handle.readlines():
                path = line.strip().split("/")
                this_files.append("/".join(path[-2:]))
            files[name] = np.array(this_files)

    files["disk"].sort()
    files["tape"].sort()

    print(run)
    assert (files["disk"] == files["tape"]).all()
