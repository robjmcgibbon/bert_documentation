#!/usr/bin/env python3

"""
plot_map.py

General functions that can be used to read and plot .npz image maps.

These functions assume that the .npz files have been generated using the
scripts in ZoomMaps/ and have a name that matches one of the following patterns:
 - L<boxsize>_8192_<component>_map_<maptype>.npz
 - L<boxsize>_8192_<component>_<maptype>.npz
where <boxsize> is the size of the simulation box in Mpc, <component> is one
of "gas", "dm", "star" or "neutrinoNS", and <maptype> is one of "sigma",
"temp" or "xray".
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pl
import unyt
import re
from swiftsimio.visualisation.tools.cmaps import LinearSegmentedCmap2D
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

# regular expressions used to obtain information from map file names.
boxsize_re = re.compile("L(\d+)\_8192")
label_re = re.compile("L\d+\_8192\_([a-zA-Z]+)\_map\_([a-zA-Z]+)\.npz")
label_re2 = re.compile("L\d+\_8192\_([a-zA-Z]+)\_([a-zA-Z]+)\.npz")

# background neutrino surface density
# value based on z=0 for the FLAMINGO cosmology
# assumes a fixed slice width in the projection direction of 20 Mpc
rho_crit = 12.87106552 * (1.0e10 * unyt.Msun) / unyt.Mpc**3
omega_nu = 0.00138908
rho_nu = rho_crit * omega_nu
sigma_nu = rho_nu * (20.0 * unyt.Mpc)
sigma_nu.convert_to_base("galactic")

# 2D gas surface density - temperature colour map (gas_temperature_map)
# we go from black for low density, cold gas to white for high density, hot gas
# high density, cold gas is blue and low density, hot gas is red
# while it is impossible to capture this in a 1D colour bar per variable,
# we mimic this by using a black-white density colour bar and a blue-red
# temperature colour bar (gas_map and temperature_map)
gas_temperature_map = LinearSegmentedCmap2D(
    colors=[[0.0, 0.0, 0.0], [0.2, 0.5, 1.0], [1.0, 0.3, 0.1], [1.0, 1.0, 1.0]],
    coordinates=[[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]],
    name="gas_temperature_map",
)
gas_map = LinearSegmentedColormap(
    name="gas_map",
    segmentdata={
        "red": [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
        "green": [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
        "blue": [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
    },
)
temperature_map = LinearSegmentedColormap(
    name="temperature_map",
    segmentdata={
        "red": [(0.0, 0.2, 0.2), (1.0, 1.0, 1.0)],
        "green": [(0.0, 0.5, 0.5), (1.0, 0.3, 0.3)],
        "blue": [(0.0, 1.0, 1.0), (1.0, 0.1, 0.1)],
    },
)


def get_label_fraction(box_size):
    """
    Get an appropriate size (as a fraction of the box size) for the ruler
    that indicates the spatial scale of the map.

    We take 20% of the box size, and then round this to the nearest power of 10.
    If the resulting fraction is larger than 40% of the box size, we half it.
    """
    label_size = 0.2 * box_size
    label_size = np.log10(label_size)
    label_size = np.round(label_size)
    label_size = 10.0**label_size
    if hasattr(box_size, "units"):
        label_size *= box_size.units
    label_fraction = label_size / box_size
    if label_fraction > 0.4:
        label_fraction *= 0.5
    return label_fraction


def extract_boxsize(name):
    """
    Extract the box size (in Mpc) from a .npz file name, assuming one of the
    following name patterns:
     - L<boxsize>_8192_<component>_map_<maptype>.npz
     - L<boxsize>_8192_<component>_<maptype>.npz
    """
    return float(boxsize_re.search(name).groups()[0])


def extract_label(name):
    """
    Extract a variable name from a .npz file name, assuming one of the
    following name patterns:
     - L<boxsize>_8192_<component>_map_<maptype>.npz
     - L<boxsize>_8192_<component>_<maptype>.npz

    We use the following name conversions (maptype -> label)
     - sigma: surface density
     - xray: X-ray luminosity
     - temp: temperature
    """
    match = label_re.search(name)
    if match is None:
        match = label_re2.search(name)
    groups = match.groups()
    type = groups[0]
    quantity = {
        "sigma": "surface density",
        "xray": "X-ray luminosity",
        "temp": "temperature",
    }[groups[1]]
    return f"{type} {quantity}"


def get_units(mapname):
    """
    Get the appropriate units for a map name.

    Note that map names are the names as used internally in the .npz files;
    they are different from the maptypes used in the .npz file names.
    """
    return {
        "surfdens": unyt.g / unyt.cm**2,
        "temp": unyt.K,
        "rosat": unyt.erg / unyt.s,
    }[mapname]


def get_data(input_name, add_neutrino_correction=False):
    """
    Get the data from a given .npz file.
    The units are deduced automatically from the internal map name in the .npz
    file.

    Optionally add the (globally defined) neutrino correction.
    """
    with np.load(input_name) as datafile:
        mapname = datafile.files[0]
        data = datafile[mapname] * get_units(mapname)
    if add_neutrino_correction:
        data += sigma_nu
    data.convert_to_base("galactic")
    return data


def get_limits(data):
    """
    Get appropriate upper and lower limits for the given map data.

    We assume all data will be plotted on a logarithmic scale, so negative
    values are excluded.
    If the data spans more than 15 dex, we impose vmin = vmax - 15 dex.
    """
    vmin = data.min()
    vmax = data.max()
    if vmin <= 0.0:
        vmin = data[data > 0].min()
    if np.log10(vmax) - np.log10(vmin) > 15.0:
        vmin = 1.0e-15 * vmax
    return vmin, vmax


def plot_map_on_axis(map, ax, whole_extent, actual_extent=None, shift=None):
    """
    Plot the given map (RGBA pixel values) on the given axis.

    STILL USED?
    """
    if actual_extent is None:
        actual_extent = whole_extent

    boxsize = actual_extent[1] - actual_extent[0]

    mapcopy = map.copy()
    if shift is not None:
        xshift = int(shift[0] / boxsize * map.shape[0])
        yshift = int(shift[1] / boxsize * map.shape[1])
        mapcopy = np.roll(mapcopy, (xshift, yshift), axis=(1, 0))

    vals = ax.imshow(
        mapcopy,
        origin="lower",
        extent=whole_extent,
    )

    # plot the scale label
    x = actual_extent[0]
    y = actual_extent[2]
    label_fraction = get_label_fraction(boxsize)
    scale_label = f"{label_fraction*boxsize:.0f}"
    if not hasattr(boxsize, "units"):
        scale_label += " Mpc"
    ax.plot(
        [x + 0.05 * boxsize, x + (0.05 + label_fraction) * boxsize],
        [y + 0.05 * boxsize, y + 0.05 * boxsize],
        "w-",
        linewidth=4,
    )
    ax.text(
        x + 0.05 * boxsize,
        y + 0.07 * boxsize,
        scale_label,
        color="w",
    )

    return vals


def create_map(data, lims, labels):
    if len(data) == 1:
        norm = matplotlib.colors.LogNorm(lims[0][0], lims[0][1])
        cmap = matplotlib.get_cmap("viridis")
        return cmap(norm(data[0].T)), cmap, lims[0]
    else:
        if len(labels) == 2:
            if not "gas surface density" in labels or not "gas temperature" in labels:
                raise RuntimeError(
                    f"Cannot combine '{labels[0]}' and '{labels[1]}' into a single map!"
                )
        scaled_data = []
        plot_lims = []
        for d, minmax in zip(data, lims):
            norm = matplotlib.colors.LogNorm(minmax[0], minmax[1])
            scaled_data.append(norm(d.T))
            plot_lims.append(minmax)
        if labels[0] == "gas temperature":
            scaled_data = [scaled_data[1], scaled_data[0]]
            plot_lims = [plot_lims[1], plot_lims[0]]
        return gas_temperature_map(*scaled_data), [gas_map, temperature_map], plot_lims


def plot_data_on_axis(
    data,
    vmin,
    vmax,
    ax,
    whole_extent,
    actual_extent=None,
    shift=None,
    scale_label=True,
    cmap="viridis",
):
    """
    Plot the given map data on the given axis, using the given data limits and
    spatial extent.

    The data limits are given as vmin and vmax.
    The map data covers a certain spatial region (whole_extent), but we might
    not want to plot that entire region (actual_extent). When a shift is given,
    the whole map is periodically shifted before the visualisation.
    The map is plotted with a scale indication (scale_label), and with the
    given colour map (cmap).

    Returns the AxesImage returned by matplotlib.imshow(). Can be used to
    create a colour bar based on the image.
    """

    # attach missing units
    if not hasattr(vmin, "units"):
        vmin = vmin * data.units
    if not hasattr(vmax, "units"):
        vmax = vmax * data.units

    # plot the whole extent if no actual extent is requested
    if actual_extent is None:
        actual_extent = whole_extent

    # get the box size from the extent
    boxsize = actual_extent[1] - actual_extent[0]

    # make a copy of the data to avoid overwriting the original
    # then apply the shift, if one has been requested
    datacopy = data.copy()
    if shift is not None:
        xshift = int(shift[0] / boxsize * data.shape[0])
        yshift = int(shift[1] / boxsize * data.shape[1])
        datacopy = np.roll(datacopy, (xshift, yshift), axis=(0, 1))

    # plot the map
    vals = ax.imshow(
        datacopy.T,
        origin="lower",
        norm=matplotlib.colors.LogNorm(vmin.to(data.units), vmax.to(data.units)),
        extent=whole_extent,
        cmap=cmap,
    )

    # plot the scale label
    if scale_label:
        x = actual_extent[0]
        y = actual_extent[2]
        label_fraction = get_label_fraction(boxsize)
        scale_label = f"{label_fraction*boxsize:.0f}"
        if not hasattr(boxsize, "units"):
            scale_label += " Mpc"
        ax.add_artist(
            AnchoredSizeBar(
                ax.transData,
                boxsize * label_fraction,
                scale_label,
                "lower left",
                size_vertical=0.02,
                label_top=True,
                color="white",
                frameon=False,
            )
        )

    return vals


def plot_single_map(
    input_names, output_name, boxsize=None, label=None, add_neutrino_correction=False
):

    data = [get_data(input_name, add_neutrino_correction) for input_name in input_names]

    if boxsize is None:
        boxsize = extract_boxsize(input_names[0])
        for i in range(1, len(input_names)):
            assert boxsize == extract_boxsize(input_names[i])

    if label is None:
        labels = [extract_label(input_name) for input_name in input_names]
    else:
        labels = [label] * len(input_names)

    lims = [get_limits(d) for d in data]

    pl.rcParams["text.usetex"] = True

    map, cmaps, lims = create_map(data, lims, labels)
    print(map.shape)

    fig, ax = pl.subplots()

    vals = plot_map_on_axis(map, ax, [0.0, boxsize, 0.0, boxsize])
    for i in range(len(data)):
        vals = matplotlib.cm.ScalarMappable(
            norm=matplotlib.colors.LogNorm(*lims[i]), cmap=cmaps[i]
        )
        fig.colorbar(vals, label=f"{labels[i]} [${data[i].units.latex_repr}$]")
    ax.set_xlabel("$x$ [Mpc]")
    ax.set_ylabel("$y$ [Mpc]")

    pl.tight_layout()
    pl.savefig(output_name, dpi=300)
    pl.close()


if __name__ == "__main__":

    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("input", nargs="+")
    argparser.add_argument("output")
    argparser.add_argument("--boxsize_in_Mpc", "-b", type=float)
    argparser.add_argument("--label", "-l")
    argparser.add_argument("--neutrinos", action="store_true")
    args = argparser.parse_args()

    plot_single_map(
        args.input, args.output, args.boxsize_in_Mpc, args.label, args.neutrinos
    )
