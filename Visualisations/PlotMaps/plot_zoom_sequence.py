#!/usr/bin/env python3

"""
plot_zoom_sequence.py

Plot a series of inset zoom images based on pre-computed images in .npz files.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pl
import unyt
from plot_map import get_data, get_limits, plot_data_on_axis

## global parameters (can be changed freely):

# run the script in "dummy" mode? This uses random image data instead of .npz
# file data, making the script a lot faster to run. Useful for testing and
# fine-tuning of plots.
dummy = False
# simulation to plot (possible options: L1000 or L2800)
sim = "L2800"
# how many levels of zoom to add (0-2)
# useful for producing a series of images where additional zoom levels are
# added sequentially
level = 2

# colour used from the frame for zoom insets and for connecting lines
linecolor = "white"
# manually overwrite the data limits?
vmin_fixed = None
vmax_fixed = None

## additional parameters (do not change, unless you know what you are doing)

# simulation specific variables
if sim == "L1000":
    # path to the .npz files
    path = "L1000_zooms/L1000N3600"
    # suffix used in image file names
    output_suffix = "L1000N3600"
    # box size of the simulation
    boxsize = 1000.0 * unyt.Mpc
    # box size of the various zoom images in the .npz files
    zooms = {
        "L1000": 1000.0 * unyt.Mpc,
        "L250": 250.0 * unyt.Mpc,
        "L63": 63.0 * unyt.Mpc,
    }
    # box size for the different images that are actually plotted
    targets = unyt.unyt_array([1000.0, 100.0, 25.0], units="Mpc")
    # additional shift for the large image, useful to move the massive cluster
    # in the centre away from the centre, where it would be hidden by the zoom
    # insets
    big_shift = (-200.0 * unyt.Mpc, 0.0 * unyt.Mpc)
elif sim == "L2800":
    path = "L2800_zooms/L2800N5040"
    output_suffix = "L2800N5040"
    boxsize = 2800.0 * unyt.Mpc
    zooms = {
        "L2800": 2800.0 * unyt.Mpc,
        "L700": 700.0 * unyt.Mpc,
        "L175": 175.0 * unyt.Mpc,
        "L45": 45.0 * unyt.Mpc,
    }
    zoomfac = np.sqrt(2800.0 / 20.0)
    targets = unyt.unyt_array([2800.0, 2800.0 / zoomfac, 20.0], units="Mpc")
    print(targets)
    big_shift = (-500.0 * unyt.Mpc, 0.0 * unyt.Mpc)
else:
    raise RuntimeError(f"Unknown sim: '{sim}'")


def get_closest_map(target_size):
    """
    Get the closest existing .npz map to the given target box size.

    Closest means: the smallest map that has a size equal to or larger than the
    target, so that the target size is completely contained within the map.

    Returns the name of the map (.npz file name) and the extents of the spatial
    region covered by that map.
    """
    mapnames = list(zooms.keys())
    for izoom, zoom in enumerate(mapnames):
        if target_size > zooms[zoom]:
            break
    if target_size > zooms[zoom]:
        map = mapnames[max(izoom - 1, 0)]
    else:
        map = mapnames[izoom]
    box = zooms[map]
    xm = 0.5 * (boxsize - box)
    xp = xm + box
    return map, unyt.unyt_array([xm, xp, xm, xp])


def plot_square(ax, extent):
    """
    Plot a square with the given extent on the given axis.
    """
    xm = extent[0]
    xp = extent[1]
    ym = extent[2]
    yp = extent[3]
    ax.plot([xm, xm, xp, xp, xm], [ym, yp, yp, ym, ym], "-", color=linecolor)


# loop over all components
# accumulate their maps in "total"
total = None
for type, label in [
    ("dm", "Dark matter"),
    ("gas", "Gas"),
    ("star", "Stellar"),
    ("neutrinoNS", "Neutrino"),
    ("total", "Total"),
]:

    if type == "total":
        data = total
    else:
        # get the data: find the closest map for each target and read it
        dname = "map_sigma"
        map_info = [get_closest_map(tsize) for tsize in targets]
        files = [f"{path}/{map}_8192_{type}_{dname}.npz" for map, _ in map_info]
        if not dummy:
            data = [get_data(file, type == "neutrinoNS") for file in files]
        else:
            # dummy: generate random data instead
            data = [
                unyt.unyt_array(
                    10.0 ** np.random.exponential(size=(100, 100)), units="g/cm**2"
                )
                for file in files
            ]
            # mark a square in the large map to check the positioning
            data[0][40:60, 40:60] = 1.0

    # accumulate totals for the last map
    if total is None:
        total = list(data)
    else:
        for id in range(len(data)):
            total[id] += data[id]

    # skip plotting the maps that are not "total" (for now)
    if type != "total":
        continue

    # downsample the stellar map, since it looks horrible at file resolution
    if type == "star":
        rfac = 8
        res = data[0].shape[0] // rfac
        newshape = (res, rfac, res, rfac)
        for id in range(len(data)):
            data_reshape = data[id].reshape(newshape)
            data_reshape = data_reshape.mean(axis=1)
            data_reshape = data_reshape.mean(axis=2)
            data[id] = data_reshape

    # get the limits of the data
    bounds = np.array([get_limits(d) for d in data])
    vmin = bounds[:, 0].min()
    vmax = bounds[:, 1].max()
    # overwrite the limits if requested
    if vmin_fixed is not None:
        vmin = vmin_fixed
    if vmax_fixed is not None:
        vmax = vmax_fixed

    # set up the plot(s)
    pl.rcParams["text.usetex"] = True
    pl.rcParams["font.size"] = 15

    fig, ax = pl.subplots(figsize=(8, 7))
    ax = [ax]
    if level > 0:
        ax.append(ax[0].inset_axes([0.55, 0.55, 0.4, 0.4]))
    if level > 1:
        ax.append(ax[0].inset_axes([0.55, 0.05, 0.4, 0.4]))

    # now loop over the various zoom levels and create the plots
    # we accumulate the extents to create the zoom annotations afterwards
    extents = []
    for i, d in enumerate(data):
        # skip levels that we do not want to plot
        if i > level:
            continue
        # get the extent that we want to plot
        # this can be smaller than the extent of the map that is used
        xmin = 0.5 * (boxsize - targets[i])
        xmax = xmin + targets[i]
        extent = unyt.unyt_array([xmin, xmax, xmin, xmax])
        map_extent = map_info[i][1].copy()
        # apply the requested shift to the largest map
        shift = None
        if i == 0:
            shift = big_shift
            extent[0] -= shift[0]
            extent[1] -= shift[0]
            extent[2] -= shift[1]
            extent[3] -= shift[1]
            map_extent[0] -= shift[0]
            map_extent[1] -= shift[0]
            map_extent[2] -= shift[1]
            map_extent[3] -= shift[1]
        extents.append(extent)
        print(map_extent, extent)
        # plot the data on this level
        vals = plot_data_on_axis(d, vmin, vmax, ax[i], map_extent, extent, shift=shift)
        # set the appropriate extent on the axis
        ax[i].set_xlim(extent[0], extent[1])
        ax[i].set_ylim(extent[2], extent[3])
        # some additional axis configuration
        ax[i].axis("off")
        ax[i].set_aspect("equal")

    # add zoom annotations: a frame around the inset panels and zoom indication
    # lines linking the larger map with the zoom image
    if level > 0:
        plot_square(ax[1], extents[1])
        ax[0].indicate_inset_zoom(ax[1], edgecolor=linecolor, linewidth=1.0)
    if level > 1:
        plot_square(ax[2], extents[2])
        ax[1].indicate_inset_zoom(ax[2], edgecolor=linecolor, linewidth=1.0)

    # set appropriate "extend" values for the colour bar, depending on which
    # limits were manually overwritten
    if vmin_fixed is None:
        if vmax_fixed is None:
            extend = "neither"
        else:
            extend = "max"
    else:
        if vmax_fixed is None:
            extend = "min"
        else:
            extend = "both"

    # add the colour bar
    fig.colorbar(
        vals,
        ax=ax[0],
        label=f"{label} surface density [M$_\\odot$/kpc$^{2}$]",
        aspect=25,
        shrink=0.9,
        extend=extend,
    )

    # finish and save the plot
    pl.tight_layout()
    suffix = ["none", "half", "full"][level]
    pl.savefig(
        f"sequence/zoom_sequence_{output_suffix}_{type}_{suffix}.png",
        dpi=300,
        bbox_inches="tight",
    )
    # stop here if we are only testing things
    if dummy:
        exit()
