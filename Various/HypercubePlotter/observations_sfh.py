#!/usr/bin/env python3

"""
observations_sfh.py

Adds the cosmic star formation history data of Behroozi (2019) to a plot.

This script cannot be run directly, but has to be read in and then executed
using `exec()`, in an environment that has a Matplotlib.Axis variable `ax`
defined.
"""

def add_sfh_data(ax):
    for style, label in [("-", "true"), ("--", "observed")]:
        obs = load_observations(
            f"pipeline-configs/observational_data/data/StarFormationRateHistory/Behroozi2019_{label}.hdf5"
        )[0]

        a = obs.x.value
        sfh = obs.y
        ax.plot(
            1.0 / a - 1.0,
            sfh,
            f"k{style}",
            alpha=0.5,
            label=obs.citation,
            zorder=-10000,
        )
    ax.set_xlabel("Redshift")


add_sfh_data(ax)
