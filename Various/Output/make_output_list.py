#!/usr/bin/env python3

"""
make_output_list.py

Convert table information from 4 separate .txt files (copied straight over
from the COLIBRE spreadsheet) into a .yml file that is compatible with SWIFT.

All file names have been hard-coded. This script assumes the table structure
as it was on December 23rd, 2022.
"""

import numpy as np

parttypes = ["Gas", "DM", "Stars", "BH"]

with open("colibre_default_output_list.yml", "w") as handle:
    handle.write("Default:\n")
    for partname in parttypes:
        handle.write(f"  # {partname} properties:\n")
        data = np.loadtxt(
            f"{partname}.txt",
            usecols=(0, 1, 3),
            dtype=[("Name", "U100"), ("Size", np.uint8), ("Compression", "U100")],
            delimiter="\t",
        )
        for d in data:
            name = d["Name"]
            if d["Size"] == 0:
                val = "off"
            else:
                if d["Compression"] == "None":
                    val = "on"
                else:
                    val = d["Compression"]
            handle.write(f"  {name}_{partname}: {val}\n")
        handle.write("\n")
