#!/usr/bin/env python3

"""
fix_catalogue_names.py

Solution for a bug in an early hypercube run: a missing '@' in one of the
template VR job scripts had caused all the VR output to be wrongly named
'@SNAP' instead of '2729'.

Meant as an example of how to efficiently deal with such issues.
"""

import glob
import os

files = sorted(glob.glob("wdir_*/halos*@SNAP*"))

for file in files:
    new_file = file.replace("@SNAP", "2729")
    print(f"{file} --> {new_file}")
    os.rename(file, new_file)
