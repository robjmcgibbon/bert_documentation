#!/usr/bin/env python3

"""
convert_gas_evolution.py

Adapted version of the gas evolution script in the COLIBRE pipeline that
creates a `.yml` file for the rhoHI and rhoH2 evolution plots.

Usage:
  python3 convert_gas_evolution.py STATISTICS SNAPSHOT OUTPUT
where
 - STATISTICS is the `statistics.txt` output file for a simulation
 - SNAPSHOT is an arbitrary snapshot for the same simulation (used to get the
   box size and units)
 - OUTPUT is the name of the `.yml` output file
"""

import unyt
import numpy as np
import yaml
from scipy import stats

from swiftsimio import load, load_statistics


rho_unit = "Msun/Mpc**3"


def load_data(stats_filename, snapshot_filename):

    data = load_statistics(stats_filename)

    snapshot = load(snapshot_filename)
    units = snapshot.units
    boxsize = snapshot.metadata.boxsize
    box_volume = boxsize[0] * boxsize[1] * boxsize[2]

    scale_factor = data.a
    rhoHI = (data.gas_hi_mass / box_volume).to(rho_unit)
    rhoH2 = (data.gas_h2_mass / box_volume).to(rho_unit)

    # a, Redshift, SFR
    return scale_factor, rhoHI, rhoH2


if __name__ == "__main__":

    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("statsfile")
    argparser.add_argument("snapshotfile")
    argparser.add_argument("outputfile")
    args = argparser.parse_args()

    magnitudes = np.logspace(-2, np.log10(20), 50)
    magnitudes_centres = 0.5 * (magnitudes[:-1] + magnitudes[1:])

    scale_factor, rho_HI, rho_H2 = load_data(args.statsfile, args.snapshotfile)

    rhoHI_median, _, _ = stats.binned_statistic(
        1.0 / scale_factor - 1.0, rho_HI.value, statistic="median", bins=magnitudes
    )
    rhoHI_16, _, _ = stats.binned_statistic(
        1.0 / scale_factor - 1.0,
        rho_HI.value,
        statistic=lambda x: np.percentile(x, 16.0),
        bins=magnitudes,
    )
    rhoHI_84, _, _ = stats.binned_statistic(
        1.0 / scale_factor - 1.0,
        rho_HI.value,
        statistic=lambda x: np.percentile(x, 84.0),
        bins=magnitudes,
    )
    mask = (
        (~np.isnan(rhoHI_median))
        & (~np.isnan(rhoHI_16))
        & (~np.isnan(rhoHI_84))
        & (rhoHI_median > 0.0)
    )
    mask_val = 0.1 * rhoHI_median[mask].min()
    rhoHI_median[~mask] = mask_val
    rhoHI_16[~mask] = mask_val
    rhoHI_84[~mask] = mask_val
    rhoHI_err = np.zeros((2, rhoHI_16.shape[0]))
    rhoHI_err[0, :] = rhoHI_median - rhoHI_16
    rhoHI_err[1, :] = rhoHI_84 - rhoHI_median

    rhoH2_median, _, _ = stats.binned_statistic(
        1.0 / scale_factor - 1, rho_H2.value, statistic="median", bins=magnitudes
    )
    rhoH2_16, _, _ = stats.binned_statistic(
        1.0 / scale_factor - 1.0,
        rho_H2.value,
        statistic=lambda x: np.percentile(x, 16.0),
        bins=magnitudes,
    )
    rhoH2_84, _, _ = stats.binned_statistic(
        1.0 / scale_factor - 1.0,
        rho_H2.value,
        statistic=lambda x: np.percentile(x, 84.0),
        bins=magnitudes,
    )
    mask = (
        (~np.isnan(rhoH2_median))
        & (~np.isnan(rhoH2_16))
        & (~np.isnan(rhoH2_84))
        & (rhoH2_median > 0.0)
    )
    mask_val = 0.1 * rhoH2_median[mask].min()
    rhoH2_median[~mask] = mask_val
    rhoH2_16[~mask] = mask_val
    rhoH2_84[~mask] = mask_val
    rhoH2_err = np.zeros((2, rhoH2_16.shape[0]))
    rhoH2_err[0, :] = rhoH2_median - rhoH2_16
    rhoH2_err[1, :] = rhoH2_84 - rhoH2_median

    data = {
        "rhoHI": {
            "lines": {
                "median": {
                    "centers": magnitudes_centres.tolist(),
                    "bins": magnitudes.tolist(),
                    "centers_units": "dimensionless",
                    "values": rhoHI_median.tolist(),
                    "values_units": rho_unit,
                    "scatter": rhoHI_err.tolist(),
                    "scatter_units": rho_unit,
                },
            },
        },
        "rhoH2": {
            "lines": {
                "median": {
                    "centers": magnitudes_centres.tolist(),
                    "bins": magnitudes.tolist(),
                    "centers_units": "dimensionless",
                    "values": rhoH2_median.tolist(),
                    "values_units": rho_unit,
                    "scatter": rhoH2_err.tolist(),
                    "scatter_units": rho_unit,
                },
            },
        },
    }

    with open(args.outputfile, "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False)
