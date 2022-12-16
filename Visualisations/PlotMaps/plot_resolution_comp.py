#!/usr/bin/env python3

"""
plot_resolution_comp.py

Make a comparison plot of the same region of the FLAMINGO 1Gpc box, for 3
different resolution.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pl
import unyt
from plot_map import get_data, get_limits, plot_data_on_axis

# Set to True to generate fake image maps
# Useful to run some quick tests, since loading the maps is quite slow
dummy = False

# names and labels for the 3 different resolutions
names = ["L1000N3600", "L1000N1800", "L1000N0900"]
labels = ["Fid\_DES3\_L1p\_High", "Fid\_DES3\_L1p\_Int", "Fid\_DES3\_L1p\_Low"]

# extent of the box that is plotted (63 Mpc around the centre of the box)
# and position of the 4 Mpc zoom region that is focussed on a filament.
# the latter was found visually using trial and error
xmin = 0.5 * (1000.0 - 63.0)
xmax = xmin + 63.0
extent = unyt.unyt_array([xmin, xmax, xmin, xmax], units="Mpc")
zoom = unyt.unyt_array([521.0, 526.0, 513.0, 518.0], units="Mpc")

# colour of the lines and boxes used to show the zoom region
linecolor = "white"


def plot_square(ax, extent):
    """
    Plot a square with the given extent on top of the given axis.

    Used to create a border around the zoom inset images.
    """
    xm = extent[0]
    xp = extent[1]
    ym = extent[2]
    yp = extent[3]
    ax.plot(
        [xm, xm, xp, xp, xm], [ym, yp, yp, ym, ym], "-", color=linecolor, linewidth=2.0
    )


# variable in which the total mass map is accumulated
total = None
# loop over all particle species
for type, label in [
    ("dm", "Dark matter"),
    ("gas", "Gas"),
    ("star", "Stellar"),
    ("neutrinoNS", "Neutrino"),
    ("total", "Total"),
]:

    # read the map, unless it is the total map that we have calculated
    if type == "total":
        data = total
    else:
        # not the total map: read the map from the corresponding .npz file
        dname = "map_sigma"
        files = [f"L1000_zooms/{res}/L63_8192_{type}_{dname}.npz" for res in names]
        if not dummy:
            data = [get_data(file, type == "neutrinoNS") for file in files]
        else:
            # create a dummy map instead
            data = [
                unyt.unyt_array(
                    10.0 ** np.random.exponential(size=(100, 100)), units="g/cm**2"
                )
                for file in files
            ]
            data[0][40:60, 40:60] = 1.0

    # accumulate the total masses
    if total is None:
        total = list(data)
    else:
        for id in range(len(data)):
            total[id] += data[id]
    # skip maps that are not the total, since that is what we show in the paper
    if type != "total":
        continue
    # downgrade the stellar map to increase its brightness
    if type == "star":
        rfac = 8
        res = data[0].shape[0] // rfac
        newshape = (res, rfac, res, rfac)
        for id in range(len(data)):
            data_reshape = data[id].reshape(newshape)
            data_reshape = data_reshape.mean(axis=1)
            data_reshape = data_reshape.mean(axis=2)
            data[id] = data_reshape

    # get the data limits, to ensure the same colour map for the full map
    # and the zoom inset
    bounds = np.array([get_limits(d) for d in data])
    vmin = bounds[:, 0].min()
    vmax = bounds[:, 1].max()
    for d in data:
        d[d < vmin] = vmin

    # make the plot
    pl.rcParams["text.usetex"] = True
    pl.rcParams["font.size"] = 15

    fig = pl.figure(figsize=(12.5, 4))
    # we need some magic here to make the colour bar show up in the right way
    cspan = 9
    ashape = (1, 3 * cspan + 1)
    ax = [
        pl.subplot2grid(ashape, (0, 0), colspan=cspan),
        pl.subplot2grid(ashape, (0, cspan), colspan=cspan),
        pl.subplot2grid(ashape, (0, 2 * cspan), colspan=cspan),
        pl.subplot2grid(ashape, (0, 3 * cspan)),
    ]
    # inset axes are easier
    iax = [
        ax[0].inset_axes([0.6, 0.05, 0.35, 0.35]),
        ax[1].inset_axes([0.6, 0.05, 0.35, 0.35]),
        ax[2].inset_axes([0.6, 0.05, 0.35, 0.35]),
    ]

    # loop over the different resolutions, since we always do the same to plot
    # them, but then on a different axis
    for i, d in enumerate(data):
        # delegate the actual plotting to plot_data_on_axis()
        vals = plot_data_on_axis(d, vmin, vmax, ax[i], extent)
        # plot the simulation name label
        ax[i].text(
            0.5,
            0.93,
            labels[i],
            color="white",
            transform=ax[i].transAxes,
            horizontalalignment="center",
        )
        ax[i].axis("off")

        # now plot the zoom map
        plot_data_on_axis(d, vmin, vmax, iax[i], extent, actual_extent=zoom)
        iax[i].set_xlim(zoom[0], zoom[1])
        iax[i].set_ylim(zoom[2], zoom[3])
        iax[i].axis("off")

        # create a border for the zoom image and make a nice zoom indication
        # in the parent image
        plot_square(iax[i], zoom)
        ax[i].indicate_inset_zoom(iax[i], edgecolor=linecolor, linewidth=2.0)

    # add the colour bar
    fig.colorbar(
        vals,
        cax=ax[3],
        label=f"{label} surface density [M$_\\odot$/kpc$^{2}$]",
    )

    # save the figure
    pl.tight_layout()
    pl.savefig(f"compare_resolutions_{type}.png", dpi=300, bbox_inches="tight")
    # close the figure, in case we are plotting multiple components
    pl.close(fig)
