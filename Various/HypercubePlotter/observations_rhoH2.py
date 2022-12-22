#!/usr/bin/env python3

"""
observations_rhoH2.py

Adds the H2 evolution data of Walter (2020) to a plot.

This script cannot be run directly, but has to be read in and then executed
using `exec()`, in an environment that has a Matplotlib.Axis variable `ax`
defined.
"""

def add_rhoH2_data(ax):
    obs = load_observations(
        f"pipeline-configs/observational_data/data/CosmicH2Abundance/Walter2020.hdf5"
    )[0]

    a = obs.x.value
    rhoH2_low = obs.y - obs.y_scatter[0]
    rhoH2_high = obs.y + obs.y_scatter[1]
    ax.fill_between(
        1.0 / a - 1.0,
        rhoH2_low,
        rhoH2_high,
        color="k",
        alpha=0.5,
        label=obs.citation,
        zorder=-10000,
    )
    ax.set_xlabel("Redshift")


add_rhoH2_data(ax)
