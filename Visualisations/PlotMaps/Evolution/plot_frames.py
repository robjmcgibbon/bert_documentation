import astropy.cosmology
import numpy as np
import multiprocessing as mp
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pl
import yaml
import argparse
import os
from swiftsimio.visualisation.tools.cmaps import LinearSegmentedCmap2D

gas_temperature_map = LinearSegmentedCmap2D(
    colors=[[0.0, 0.0, 0.0], [0.2, 0.5, 1.0], [1.0, 0.3, 0.1], [1.0, 1.0, 1.0]],
    coordinates=[[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]],
    name="gas_temperature_map",
)
dm_map = pl.get_cmap("cividis")
xray_map = pl.get_cmap("magma")
# star_map = pl.get_cmap("pink")
star_map = pl.get_cmap("gist_gray")

square = True

def read_map(filename, mapname, selection=None):
    data = np.load(filename)[mapname]
    if mapname == "surfdens":
      dmean = data.mean()
      if dmean > 0.:
        data /= dmean
    if selection is None:
        return data
    else:
        return data[
            selection[0] : selection[1], selection[2] : selection[3]
        ]


def get_quantity(z, quantity, limits, selection=None):

    zmin = -1000.0
    filemin = None
    zmax = 1000.0
    filemax = None
    for file in limits:
        if limits[file]["fullquantity"] == quantity:
            zdiff = z - np.float32(limits[file]["redshift"])
            if zdiff <= 0.0 and zdiff > zmin:
                zmin = zdiff
                filemin = file
            elif zdiff > 0.0 and zdiff < zmax:
                zmax = zdiff
                filemax = file

    # TODO: Needed if a snapshot exists for DM but not for stars
    if filemin is None:
        return read_map(filemax, limits[filemax]["quantity"], selection)

    if filemax is None:
        return read_map(filemin, limits[filemin]["quantity"], selection)

    mapmin = read_map(filemin, limits[filemin]["quantity"], selection)
    mapmax = read_map(filemax, limits[filemax]["quantity"], selection)

    a = 1.0 / (1.0 + z)
    amin = 1.0 / (1.0 + z - zmin)
    amax = 1.0 / (1.0 + z - zmax)

    fac = (a - amin) / (amax - amin)

    mapdata = (1.0 - fac) * mapmin + fac * mapmax

    del mapmin
    del mapmax

    return mapdata


def get_quantities(q):
    return {
        "dm": ["dm/surfdens"],
        "gas": ["gas/surfdens", "gas/temp"],
        "xray": ["gas/rosat"],
        "star": ["star/surfdens"],
    }[q]


def combine_maps(q, maps, quantities):
    if q == "dm":
        return dm_map(maps[0].T)
    elif q == "gas":
        return gas_temperature_map(maps[0].T, maps[1].T)
    elif q == "xray":
        return xray_map(maps[0].T)
    elif q == "star":
        return star_map(maps[0].T)
    else:
        raise RuntimeError(f"Unknown quantity: {q}!")


def make_frames(args):

    idx, z, quantities, limits, outputfolder, quantity, selection = args

    output = f"{outputfolder}/{quantity}_frame_{idx:04d}.png"

    maps = []
    norms = {}
    for q in get_quantities(quantity):
        dmin = quantities[q]["min"]
        dmax = quantities[q]["max"]
        mapdata = get_quantity(z, q, limits, selection)
        if not square:
            i_cut = mapdata.shape[0] * 7 // 32
            mapdata = mapdata[:, i_cut:-i_cut]
        mapdata[mapdata <= dmin] = dmin

        if quantity == 'star':
            mapdata[mapdata > dmin] = dmax

        mapdata = matplotlib.colors.LogNorm(vmin=dmin, vmax=dmax)(mapdata)
        maps.append(mapdata)
    mapdata = combine_maps(quantity, maps, quantities)
    for map in maps:
        del map

    if square:
        fig, ax = pl.subplots(figsize=(6, 6))
    else:
        fig, ax = pl.subplots(figsize=(16, 9))

    ax.imshow(mapdata, origin="lower")

    cosmo = astropy.cosmology.FlatLambdaCDM(H0=68.1, Om0=0.306)
    age = cosmo.age(z).value
    time_label = f'Universe Age: {age:.2f} Gyr'
    # TODO: Text location for square images
    if square:
        ax.text(0.02, 0.05, time_label, color="w", transform = ax.transAxes)
        ax.text(0.7, 0.06, "FLAMINGO", color="w", transform = ax.transAxes)
        ax.text(0.7, 0.03, "Virgo Consortium", color="w", transform = ax.transAxes)
    else:
        ax.text(0.02, 0.05, time_label, color="w",
                transform = ax.transAxes, fontsize='x-large')
        ax.text(0.85, 0.08, "FLAMINGO", color="w",
                transform = ax.transAxes, fontsize='large')
        ax.text(0.85, 0.04, "Virgo Consortium", color="w",
                transform = ax.transAxes, fontsize='large')
    ax.axis("off")

    pl.tight_layout(pad=0)

    logo = pl.imread("flamingo_logo.png")
    # TODO: Flamingo logo location for square images
    if square:
        ax1 = fig.add_axes([0.90,0.02,0.1,0.1])
    else:
        ax1 = fig.add_axes([0.92,0.02,0.08,0.1])
    ax1.imshow(logo)
    ax1.axis('off')

    if square:
        pl.savefig(output, dpi=300)
    else:
        pl.savefig(output, dpi=240)
    fig.clear()
    pl.close(fig)

    del mapdata

    return output


if __name__ == "__main__":

    mp.set_start_method("forkserver")

    argparser = argparse.ArgumentParser()
    argparser.add_argument("inputlimits")
    argparser.add_argument("outputfolder")
    argparser.add_argument("--nproc", "-j", type=int, default=1)
    argparser.add_argument("--nframe", "-n", type=int, default=100)
    argparser.add_argument("--imin", "-i", type=int, default=-1)
    argparser.add_argument("--imax", "-I", type=int, default=-1)
    argparser.add_argument("--selection", "-s", type=int, nargs="+", default=None)
    args = argparser.parse_args()

    os.makedirs(args.outputfolder, exist_ok=True)

    with open(args.inputlimits, "r") as handle:
        limits = yaml.safe_load(handle.read())

    files = limits.keys()

    zmax = 0
    types = ["gas", "star", "dm"]
    quantities = {}
    for file in files:
        for type in types:
            if type in file:
                break
        quantity = f"{type}/{limits[file]['quantity']}"
        limits[file]["fullquantity"] = quantity
        dmin = np.float64(limits[file]["min"])
        dmax = np.float64(limits[file]["max"])
        zmax = max(zmax, np.float32(limits[file]["redshift"]))
        if not quantity in quantities:
            quantities[quantity] = {"min": dmin, "max": dmax}
        else:
            quantities[quantity]["min"] = min(quantities[quantity]["min"], dmin)
            quantities[quantity]["max"] = max(quantities[quantity]["max"], dmax)

    for q in quantities:
        dmin = quantities[q]["min"]
        dmax = quantities[q]["max"]
        if dmin == 0.0:
            dmin = 1.0e-9 * dmax
        quantities[q]["min"] = dmin

    quantities["gas/temp"]["min"] = 1.0e4
    quantities["gas/temp"]["max"] = 1.0e7

    a_range = np.linspace(1.0 / (1 + zmax), 1.0, args.nframe)
    z_range = 1.0 / a_range - 1.0

    arglist = []
    for idx, z in enumerate(z_range):
        if args.imin >= 0 and idx < args.imin:
            continue
        if args.imax >= 0 and idx >= args.imax:
            continue
        for q in ["dm", "gas", "star", "xray"]:
            arglist.append(
                (idx, z, quantities, limits, args.outputfolder, q, args.selection)
            )

    pool = mp.Pool(args.nproc)
    for frame in pool.imap_unordered(make_frames, arglist):
        print(frame)
