#!/usr/bin/env python3

"""
generate_output_report.py

Read all the datasets of all the particle types of interest and store metadata
about them into colibre_actual_output.yml.
All file names are currently hard-coded into this script.
"""

import h5py
import yaml

ptypes = ["Gas", "DM", "Stars", "BH"]

dsets = {}
with h5py.File("colibre_0002.hdf5", "r") as handle:
    for ptype in ptypes:
        dsets[ptype] = {}
        for dsetname in handle[f"{ptype}Particles"].keys():
            dset = handle[f"{ptype}Particles/{dsetname}"]
            shape = dset.shape
            if len(shape) > 1:
                shape = shape[1]
            else:
                shape = 1
            dtype = dset.dtype.name
            compression = dset.attrs["Lossy compression filter"].decode("utf-8")
            print(dsetname, shape, dtype, compression)
            dsets[ptype][f"{dsetname}_{ptype}"] = {
                "shape": shape,
                "type": dtype,
                "compression": compression,
            }

with open("colibre_actual_output.yml", "w") as handle:
    yaml.safe_dump(dsets, handle)
