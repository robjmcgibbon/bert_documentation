#!/usr/bin/env python3

"""
choose_halo.py

Script that can be used to plot a subset of halos within a mass range.
Useful for choosing a halo for a figure.
"""

import numpy as np
import h5py
import swiftsimio as sw
from swiftsimio.visualisation.projection import project_gas
import unyt
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pl

# seed the random number generator
# we need to do this to make sure the halo choice is reproducible
np.random.seed(42)

# path to the SOAP catalogue and the snapshot
cat = "/cosma8/data/dp004/dc-vand2/FLAMINGO/ScienceRuns/L1000N3600/HYDRO_FIDUCIAL/SOAP/halo_properties_0078.hdf5"
snap = "/cosma8/data/dp004/flamingo/Runs/L1000N3600/HYDRO_FIDUCIAL/snapshots/flamingo_0078/flamingo_0078.hdf5"

# read the SOAP catalogue
pos = None
with h5py.File(cat, "r") as handle:
    M200 = handle["SO/200_crit/TotalMass"][:]
    CoP = handle["VR/CentreOfPotential"][:]

    # create a random number for each halo
    rand = np.random.random(M200.shape)

    # mask out halos in a mass range; pick a 1% random subset
    mask = (M200 >= 1.0e14) & (M200 <= 2.0e14) & (rand < 0.01)
    # store the position of the matching halos
    pos = CoP[mask] * unyt.Mpc

# visualise the halo selection
for ihalo, p in enumerate(pos):
    mask = sw.mask(snap)
    b = mask.metadata.boxsize
    # load a 50 Mpc box surrounding the halo
    xmin = p - 25.0 * unyt.Mpc
    xmax = p + 25.0 * unyt.Mpc

    load_region = [[xmin[0], xmax[0]], [xmin[1], xmax[1]], [xmin[2], xmax[2]]]
    mask.constrain_spatial(load_region)

    data = sw.load(snap, mask=mask)

    # recentre the coordinates to put the halo in the centre of the box
    data.gas.coordinates[:, :] += 0.5 * b[None, :] - p[None, :]
    data.gas.coordinates = np.mod(data.gas.coordinates, b[None, :])

    # create the image
    img = project_gas(
        data,
        resolution=1024,
        project="masses",
        parallel=True,
        region=[
            -25.0 * unyt.Mpc,
            25.0 * unyt.Mpc,
            -25.0 * unyt.Mpc,
            25.0 * unyt.Mpc,
            -25.0 * unyt.Mpc,
            25.0 * unyt.Mpc,
        ],
    )

    pl.imshow(img.T, origin="lower", norm=matplotlib.colors.LogNorm())
    pl.axis("off")
    pl.tight_layout()
    pl.savefig(f"halos/halo_{ihalo:03d}.png", dpi=300, bbox_inches="tight")
    pl.close()
