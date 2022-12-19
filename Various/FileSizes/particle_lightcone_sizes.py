#!/usr/bin/env python3

"""
particle_lightcone_sizes.py

Create an overview of all the datasets that are in the FLAMINGO particle
lightcones and their actual storage size on disk.
Datasets and sizes are written to `lightcone_sizes.yml`, which can be analysed
with the `particle_lgithcone_summary.py` script.
"""

import numpy as np
import h5py
import glob
import yaml

path = "/cosma8/data/dp004/flamingo/Runs/L2800N5040/HYDRO_FIDUCIAL/lightcones/lightcone0_particles"

files = sorted(glob.glob(f"{path}/lightcone0*.hdf5"))

# parsing the full particle lightcone is very expensive, so we use a random
# 1% subset. Fix the seed for reproducibility.
np.random.seed(42)

sizes = {}
tot_size_vel = 0
tot_size_novel = 0
nfile = 0
for file in files:
    # skip 99% of the files
    if np.random.random() > 0.01:
        continue
    nfile += 1
    with h5py.File(file, "r") as handle:
        # loop over all particle groups
        for group in ["BH", "DM", "Gas", "Neutrino", "Stars"]:
            if group in handle:
                if not group in sizes:
                    sizes[group] = {}
                size_vel = 0
                size_novel = 0
                for dset in handle[group].keys():
                    if not dset in sizes[group]:
                        sizes[group][dset] = 0
                    # h5py.Dataset.id.get_storage_size() contains the actual size on disk
                    # (in bytes) of the dataset. That is what we want.
                    size = handle[group][dset].id.get_storage_size()
                    sizes[group][dset] += size
                    if dset == "Velocities":
                        size_vel += size
                    else:
                        size_novel += size
                print(group, size_vel, size_novel, size_vel / (size_vel + size_novel))
                tot_size_vel += size_vel
                tot_size_novel += size_novel

    print(
        "All",
        tot_size_vel,
        tot_size_novel,
        tot_size_vel / (tot_size_vel + tot_size_novel),
    )

# Create the output `.yml` file
print(f"Analysed {nfile} out of {len(files)} files")
with open("lightcone_sizes.yml", "w") as handle:
    yaml.safe_dump(sizes, handle)
