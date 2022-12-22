#!/usr/bin/env python3

"""
convert_SFH.py

Create a `.yml` file for the SFH plot in the COLIBRE pipeline. Adapted from the
corresponding pipeline script.

Usage:
  python3 convert_SFH.py SFRFILE SNAPSHOT OUTPUT
where:
 - SFRFILE is the `SFR.txt` output for the simulation
 - SNAPSHOT is an arbitrary snapshot for the same simulation (used to get the
   box size and units)
 - OUTPUT is the name of the `.yml` output file
"""

import unyt
import numpy as np
import yaml
from scipy import stats

from swiftsimio import load


sfr_output_units = unyt.msun / (unyt.year * unyt.Mpc**3)


def load_data(SFR_filename, snapshot_filename):

    data = np.genfromtxt(SFR_filename).T

    snapshot = load(snapshot_filename)
    units = snapshot.units
    boxsize = snapshot.metadata.boxsize
    box_volume = boxsize[0] * boxsize[1] * boxsize[2]

    sfr_units = snapshot.gas.star_formation_rates.units

    # a, Redshift, SFR
    return data[2], data[3], (data[7] * sfr_units / box_volume).to(sfr_output_units)


if __name__ == "__main__":

    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("SFRfile")
    argparser.add_argument("snapshotfile")
    argparser.add_argument("outputfile")
    args = argparser.parse_args()

    magnitudes = np.logspace(-2, np.log10(20), 50)
    magnitudes_centres = 0.5 * (magnitudes[:-1] + magnitudes[1:])

    scale_factor, redshift, sfr = load_data(args.SFRfile, args.snapshotfile)

    sfr_median, _, _ = stats.binned_statistic(
        1.0 / scale_factor - 1.0, sfr.value, statistic="median", bins=magnitudes
    )
    sfr_16, _, _ = stats.binned_statistic(
        1.0 / scale_factor - 1.0,
        sfr.value,
        statistic=lambda x: np.percentile(x, 16.0),
        bins=magnitudes,
    )
    sfr_84, _, _ = stats.binned_statistic(
        1.0 / scale_factor - 1.0,
        sfr.value,
        statistic=lambda x: np.percentile(x, 84.0),
        bins=magnitudes,
    )
    mask = (
        (~np.isnan(sfr_median))
        & (~np.isnan(sfr_16))
        & (~np.isnan(sfr_84))
        & (sfr_median > 0.0)
    )
    mask_val = 0.1 * sfr_median[mask].min()
    sfr_median[~mask] = mask_val
    sfr_16[~mask] = mask_val
    sfr_84[~mask] = mask_val
    sfr_err = np.zeros((2, sfr_16.shape[0]))
    sfr_err[0, :] = sfr_median - sfr_16
    sfr_err[1, :] = sfr_84 - sfr_16

    data = {"SFH": {}}
    data["SFH"]["lines"] = {}
    data["SFH"]["lines"]["median"] = {}
    data["SFH"]["lines"]["median"]["centers"] = magnitudes_centres.tolist()
    data["SFH"]["lines"]["median"]["bins"] = magnitudes.tolist()
    data["SFH"]["lines"]["median"]["centers_units"] = "dimensionless"
    data["SFH"]["lines"]["median"]["values"] = sfr_median.tolist()
    data["SFH"]["lines"]["median"]["values_units"] = "Msun/yr/Mpc**3"
    data["SFH"]["lines"]["median"]["scatter"] = sfr_err.tolist()
    data["SFH"]["lines"]["median"]["scatter_units"] = "Msun/yr/Mpc**3"

    with open(args.outputfile, "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False)
