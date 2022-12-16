#!/bin/usr/env python3

"""
plot_resolution_comp_gas.py

Same as plot_resolution_comp.py, but now using a 2D gas density-temperature
colour map.
Script is largely the same as the other script, but is slightly more outdated.

The only significant difference is that we need to manually convert from data
space to colour space and then plot the resulting RGBA image using imshow.
This is also still outsourced to a function in plot_map.py.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pl
import unyt
from plot_map import get_data, get_limits, create_map, plot_map_on_axis

dummy = False

names = ["L1000N3600", "L1000N1800", "L1000N0900"]
xmin = 0.5 * (1000.0 - 63.0)
xmax = xmin + 63.0
extent = unyt.unyt_array([xmin, xmax, xmin, xmax], units="Mpc")
zoom = unyt.unyt_array([507.0, 512.0, 509.0, 514.0], units="Mpc")

linecolor = "gray"


def plot_square(ax, extent):
    xm = extent[0]
    xp = extent[1]
    ym = extent[2]
    yp = extent[3]
    ax.plot([xm, xm, xp, xp, xm], [ym, yp, yp, ym, ym], "-", color=linecolor)


def connect_axes(ax1, extent, ax2, direction="right"):
    xm = extent[0]
    xp = extent[1]
    ym = extent[2]
    yp = extent[3]
    if direction == "right":
        ax1.annotate(
            "",
            xy=(xp, yp),
            xytext=(0.0, 1.0),
            xycoords=ax1.transData,
            textcoords=ax2.transAxes,
            arrowprops=dict(color=linecolor, arrowstyle="-", linewidth=1.0),
        )
        ax1.annotate(
            "",
            xy=(xp, ym),
            xytext=(0.0, 0.0),
            xycoords=ax1.transData,
            textcoords=ax2.transAxes,
            arrowprops=dict(color=linecolor, arrowstyle="-", linewidth=1.0),
        )
    elif direction == "bottom":
        ax1.annotate(
            "",
            xy=(xm, ym),
            xytext=(0.0, 1.0),
            xycoords=ax1.transData,
            textcoords=ax2.transAxes,
            arrowprops=dict(color=linecolor, arrowstyle="-", linewidth=1.0),
        )
        ax1.annotate(
            "",
            xy=(xp, ym),
            xytext=(1.0, 1.0),
            xycoords=ax1.transData,
            textcoords=ax2.transAxes,
            arrowprops=dict(color=linecolor, arrowstyle="-", linewidth=1.0),
        )
    else:
        raise AttributeError(f"Direction '{direction}' has not been implemented!")


for type, label in [
    ("gas", "Gas"),
]:

    data = {}
    for dname in ["map_sigma", "map_temp"]:
        files = [f"L1000_zooms/{res}/L63_8192_{type}_{dname}.npz" for res in names]
        if not dummy:
            data[dname] = [get_data(file) for file in files]
        else:
            data[dname] = [
                unyt.unyt_array(
                    1.0e5 * np.random.exponential(size=(100, 100)),
                    units={"map_sigma": "Msun/kpc**2", "map_temp": "K"}[dname],
                )
                for file in files
            ]

    bounds = {key: np.array([get_limits(d) for d in data[key]]) for key in data}
    vmin = {}
    vmax = {}
    for key in data:
        vmin[key] = bounds[key][:, 0].min()
        if key == "map_temp":
            vmin[key] = 1.0e5 * unyt.K
        vmax[key] = bounds[key][:, 1].max()
        for d in data[key]:
            d[d < vmin[key]] = vmin[key]

    maps = [
        create_map(
            [data["map_sigma"][i], data["map_temp"][i]],
            [
                (vmin["map_sigma"], vmax["map_sigma"]),
                (vmin["map_temp"], vmax["map_temp"]),
            ],
            ["gas surface density", "gas temperature"],
        )
        for i in range(len(data["map_sigma"]))
    ]

    pl.rcParams["text.usetex"] = True
    pl.rcParams["font.size"] = 15

    fig = pl.figure(figsize=(10, 4.4))
    rspan = 10
    ashape = (rspan + 1, 6)
    ax = [
        pl.subplot2grid(ashape, (0, 0), colspan=2, rowspan=rspan),
        pl.subplot2grid(ashape, (0, 2), colspan=2, rowspan=rspan),
        pl.subplot2grid(ashape, (0, 4), colspan=2, rowspan=rspan),
        pl.subplot2grid(ashape, (rspan, 0), colspan=3),
        pl.subplot2grid(ashape, (rspan, 3), colspan=3),
    ]
    iax = [
        ax[0].inset_axes([0.6, 0.05, 0.35, 0.35]),
        ax[1].inset_axes([0.6, 0.05, 0.35, 0.35]),
        ax[2].inset_axes([0.6, 0.05, 0.35, 0.35]),
    ]

    for i, m in enumerate(maps):
        map = m[0]
        plot_map_on_axis(map, ax[i], extent, actual_extent=extent)
        ax[i].text(
            0.5,
            0.93,
            names[i],
            color="white",
            transform=ax[i].transAxes,
            horizontalalignment="center",
        )
        ax[i].axis("off")

        plot_map_on_axis(map, iax[i], extent, actual_extent=zoom)
        iax[i].set_xlim(zoom[0], zoom[1])
        iax[i].set_ylim(zoom[2], zoom[3])
        iax[i].axis("off")

        plot_square(ax[i], zoom)
        plot_square(iax[i], zoom)
        connect_axes(ax[i], zoom, iax[i], "bottom")

    _, cmaps, lims = maps[-1]
    map_names = ["surface density [M$_\\odot$/kpc$^{2}$]", "temperature [K]"]
    for i in range(len(lims)):
        extend = "neither"
        if i == 1:
            extend = "min"
        fig.colorbar(
            matplotlib.cm.ScalarMappable(
                norm=matplotlib.colors.LogNorm(*lims[i]), cmap=cmaps[i]
            ),
            cax=ax[3 + i],
            label=f"{label} {map_names[i]}",
            extend=extend,
            orientation="horizontal",
        )

    pl.tight_layout(w_pad=0)
    pl.savefig(f"compare_resolutions_{type}.png", dpi=300)
