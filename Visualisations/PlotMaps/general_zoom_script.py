#!/usr/bin/env python3

"""
general_zoom_script.py

Create the frames for a movie that slowly zooms in on the centre of a large
box, using the images that were pre-rendered in .npz files at differnt zoom
levels.

The general idea is that all images have a sufficient resolution to allow you
to zoom at least a factor 2 to 4 on them before you start seeing pixels. At
that point, you can switch to a different image that was generated for a
smaller box, but with relatively better resolution. This repeats until you
reach the limits of the smallest box image. Because the zoom level within
a single image can vary smoothly, you can generate as many frames as you want.

To ensure a smooth transition in more challenging maps (the stellar surface
density map, which has many empty pixels), we linearly interpolate between
maps at different resolutions over a certain overlap range.

This script uses multiprocessing to generate frames in parallel. It requires
quite a lot of memory to store all the images in memory, so run it on a large
machine, like e.g. draco!
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pl
import multiprocessing as mp
from swiftsimio.visualisation.tools.cmaps import LinearSegmentedCmap2D

## input parameters

# type of map to plot
# The map type can be "stars", "xrays", "dm" or "gas"
map_type = "dm"

# do not generate the frames, but simply plot the maps next to each other to
# check the relative scaling
test_frames = False

# output prefix for frame files. Actual name will be {prefix}_XXXX.png
nframe = 1000
output_prefix = "zoom_sequence/frame"

# boxes we have
boxes = [2800.0, 700., 175.0, 45.0]
minbox = [350., 87.5, 21.875, 11.25]
box_names = ["L2800_8192", "L700_8192", "L175_8192", "L45_4096"]
#boxes = [700., 350.0, 100.0]
#box_names = ["L700_4096", "L350_3584", "L100_1024"]

# position of the zoom centre
#xt0 = 504.29982829
#yt0 = 2199.06415212
xt0 = 1400.
yt0 = 1400.
# largest and smallest zoom box size (in Mpc)
w0 = 2800.0
w1 = 20.0

# plotting limits for:
# - gas surface density (unspecified units)
smin = 2.e6
smax = 6.e10
# - dark matter surface density (unspecified units)
dmin = 1.e8
dmax = 3.e12
# - temperature (K)
Tmin = 5.e4
Tmax = 1.0e10
# - X-ray luminosities (unspecified units)
Xmax = 1.e8
Xmin = 1.0e-6 * Xmax
# - stellar surface density (unspecified units)
#stmax = 2.7884990987921e19
#stmin = 1.e14
stmax = 45307123866.25
stmin = 1.e-5*stmax
#stmin = 1.e8

# number of parallel processes to use to generate frames
nproc = 16

## other code: do not touch unless you know what you are doing!

# 2D colour map used for gas-temperature plots
gas_temperature_map = LinearSegmentedCmap2D(
    colors=[[0.0, 0.0, 0.0], [0.2, 0.5, 1.0], [1.0, 0.3, 0.1], [1.0, 1.0, 1.0]],
    coordinates=[[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]],
    name="gas_temperature_map",
)

# LogNorm() objects for all quantities
Tnrm = matplotlib.colors.LogNorm(vmin=Tmin, vmax=Tmax)
snrm = matplotlib.colors.LogNorm(vmin=smin, vmax=smax)
dnrm = matplotlib.colors.LogNorm(vmin=dmin, vmax=dmax)
Xnrm = matplotlib.colors.LogNorm(vmin=Xmin, vmax=Xmax)
stnrm = matplotlib.colors.LogNorm(vmin=stmin, vmax=stmax)

# 1D colour maps for dark matter, X-rays and stars
dmap = pl.get_cmap("cividis")
Xmap = pl.get_cmap("magma")
stmap = pl.get_cmap("pink")
#stmap = pl.get_cmap("viridis")


def get_map(folder, fac, type):
    """
    Get a map from the given folder, using the given zoom factor to rescale
    quantities to consistent units.

    The map type can be "stars", "xrays", "dm" or "gas"
    """

    if type == "stars":
        stardens = np.load(f"{folder}/star_map_sigma_z0000.npz")["surfdens"]

        nanmean = np.nanmean(stardens)
        posmin = stardens[stardens>0.].min()
        print(folder, fac, stardens.min(), stardens.max())
        print(f"{nanmean:.3e}, {fac*nanmean:.3e}")
        print(f"{posmin:.3e}, {fac*posmin:.3e}")

        stardens *= fac
        stardens[stardens <= 0.] = 1.e-99

        return stmap(stnrm(stardens.T))

    elif type == "xrays":
        xray = np.load(f"{folder}/gas_map_xray_z0000.npz")["rosat"]
        xray[xray <= 0.0] = 1.0e-99

        print(xray.min(), xray.max())

        return Xmap(Xnrm(xray.T))

    elif type == "dm":
        surfdens = np.load(f"{folder}/dm_map_sigma_z0000.npz")["surfdens"] * fac

        print(surfdens.min(), surfdens.max())

        return dmap(dnrm(surfdens.T))

    elif type == "gas":
        surfdens = np.load(f"{folder}/gas_map_sigma_z0000.npz")["surfdens"] * fac
        temp = np.load(f"{folder}/gas_map_temp_z0000.npz")["temp"]

        print(surfdens.min(), surfdens.max())

        surfdens = snrm(surfdens)
        temp = Tnrm(temp)

        return gas_temperature_map(surfdens.T, temp.T)


def get_xy(zoomfac):
    """
    Get the centre of the box at the given zoom factor.

    The centre is chosen so that it is the box centre for a zoom factor of 1,
    and equal to the chosen zoom centre for the maximum zoom factor.

    In between, it linearly moves from one to the other.
    """
    w = w0 / zoomfac
    t = (w0 - w) / (w0 - w1)
    x = (xt0 - 0.5 * w1) * t + 0.5 * w
    y = (yt0 - 0.5 * w1) * t + 0.5 * w
    return x, y, w


def plot_box(x, y, w, ax, color=None):
    """
    Plot a box with the given centre and width in the given axes with the given
    colour (or a default colour if no colour is given).
    """
    if color is None:
        ax.plot(
            [x - 0.5 * w, x + 0.5 * w, x + 0.5 * w, x - 0.5 * w, x - 0.5 * w],
            [y - 0.5 * w, y - 0.5 * w, y + 0.5 * w, y + 0.5 * w, y - 0.5 * w],
        )
    else:
        ax.plot(
            [x - 0.5 * w, x + 0.5 * w, x + 0.5 * w, x - 0.5 * w, x - 0.5 * w],
            [y - 0.5 * w, y - 0.5 * w, y + 0.5 * w, y + 0.5 * w, y - 0.5 * w],
            color=color,
        )

    return

# read the data for the frames we actually have
# each frame has a corresponding box size, map and anchor point of the map
# within the original box
maps = [None] * len(box_names)
coords = [None] * len(box_names)
for i, map in enumerate(box_names):
    fac = w0 / boxes[i]
    maps[i] = get_map(map, fac**2, map_type)
    print(maps[i].shape)
    res = maps[i].shape[0]
    x, y, _ = get_xy(fac)
    x -= 0.5 * boxes[i]
    y -= 0.5 * boxes[i]
    coords[i] = (x, y)

def get_brightness(rms):
    return np.sqrt(0.241*(rms[0]**2) + 0.691*(rms[1]**2) + 0.068*(rms[2]**2))

if test_frames:
    factors = [17.89215352740855/19.611332398104803, 1., 1., 1.]
    for i in range(len(maps)):
      fig, ax = pl.subplots(figsize=(6.,6.))
      x, y = coords[i]
      boxsize = boxes[i]
      ax.imshow(maps[i], origin="lower")
      ax.axis("off")
      ax.set_aspect("equal")
      pl.tight_layout(pad=0)
      pl.savefig(f"test_frames_{2*i:04d}.png", dpi=300)
      pl.close()
      fig, ax = pl.subplots(figsize=(6.,6.))
      xmap, ymap = coords[i]
      if i < len(maps)-1:
        x, y = coords[i+1]
        boxsize = boxes[i+1]
        other_map = np.array(maps[i+1])
      else:
        other_map = np.array(maps[i])
      this_map = np.array(maps[i])
      other_map[:,:,3] = 0.5
      ax.imshow(this_map, extent=[xmap, xmap + boxes[i], ymap, ymap + boxes[i]], origin="lower")
      ax.imshow(other_map, extent=[x, x + boxsize, y, y + boxsize], origin="lower")
#      ax.imshow(maps[i], extent=[xmap, xmap + boxes[i], ymap, ymap + boxes[i]], origin="lower")
      ax.axis("off")
      ax.set_aspect("equal")
#      ax.set_xlim(x, x + boxsize)
#      ax.set_ylim(y, y + boxsize)
      pl.tight_layout(pad=0)
      pl.savefig(f"test_frames_{2*i+1:04d}.png", dpi=300)
      pl.close()
    exit()

def get_label_fraction(box_size):
    """
    Get an appropriate size (as a fraction of the box size) for the ruler
    that indicates the spatial scale of the map
    """
    label_size = 0.2 * box_size
    label_size = np.log10(label_size)
    label_size = np.round(label_size)
    label_size = 10.0**label_size
    label_fraction = label_size / box_size
    if label_fraction > 0.4:
        label_fraction *= 0.5
    return label_fraction


def plot_frame(args):
    """
    Plot the frame with the given args:
    i: the index of the frame (used to label the resulting image file)
    fac: the zoom factor that determines the spatial scale that is plotted
    """

    i, fac = args
    # get the size of the box from the zoom factor
    boxsize = w0 / fac
    # now find the closest map in our set that is larger
    imap = len(boxes) - 1
    while boxsize > boxes[imap]:
        imap -= 1

    # get the anchor point of the closest map and of this particular box
    xmap, ymap = coords[imap]
    x, y, _ = get_xy(fac)
    x -= 0.5 * boxsize
    y -= 0.5 * boxsize

    # set up the scale label
    label_fraction = get_label_fraction(boxsize)
    scale_label = f"{label_fraction*boxsize:.0f} Mpc"

    rfac = 1
    if map_type == "stars" or map_type == "gas":
      if i == 0:
        rfac = 4
      if i == 1 or i == 2:
        rfac = 2

    # make the image
    fig, ax = pl.subplots(figsize=(6.0, 6.0))

    alphafac = 1.
    if imap > 0 and (not map_type == "gas"):
      alphafac = (boxsize-boxes[imap])/(minbox[imap-1]-boxes[imap])
      alphafac = min(1., alphafac)
      if alphafac < 1.:
        xmm1, ymm1 = coords[imap-1]
        if rfac != 1:
          res = maps[imap-1].shape[0]//rfac
          map_reshape = maps[imap-1].reshape((res, rfac, res, rfac, 4))
          map_reshape = map_reshape.max(axis=1)
          map_reshape = map_reshape.max(axis=2)
          this_map = map_reshape
        else:
          this_map = maps[imap-1]
        ax.imshow(this_map, extent=[xmm1, xmm1 + boxes[imap-1], ymm1, ymm1 + boxes[imap-1]],
                  origin="lower")

    if rfac != 1:
        res = maps[imap].shape[0]//rfac
        map_reshape = maps[imap].reshape((res, rfac, res, rfac, 4))
        map_reshape = map_reshape.max(axis=1)
        map_reshape = map_reshape.max(axis=2)
        this_map = map_reshape
    else:
        this_map = maps[imap]


    # plot the entire map with the appropriate size (set by the actual map)
    ax.imshow(
#        maps[imap],
        this_map,
        extent=[xmap, xmap + boxes[imap], ymap, ymap + boxes[imap]],
        origin="lower",
        alpha = alphafac,
    )

    # plot the scale label
    ax.plot(
        [x + 0.05 * boxsize, x + (0.05 + label_fraction) * boxsize],
        [y + 0.05 * boxsize, y + 0.05 * boxsize],
        "w-", linewidth=4
    )
    ax.text(x + 0.05 * boxsize, y + 0.07 * boxsize, scale_label, color="w", fontsize="xx-large")

    # now adjust the axis limits so that only the box of interest is shown
    ax.set_aspect("equal")
    ax.set_xlim(x, x + boxsize)
    ax.set_ylim(y, y + boxsize)

    # clean up the plot and save the frame
    ax.axis("off")
    pl.tight_layout(pad=0)
    pl.savefig(f"{output_prefix}_{i:04d}.png", dpi=300)
    pl.close()

    # return the args so that the caller can track progress
    return i, fac


# set up a parallel pool with 32 processes
pool = mp.Pool(nproc)
zfacs = np.logspace(0.0, np.log10(w0 / w1), nframe)
zfacs = [1., 4., 16., 64.]
# generate 1000 frames between a zoom factor of 1 and w0/w1 (in parallel)
for i, fac in pool.imap_unordered(
    plot_frame, enumerate(zfacs)
):
    # display some progress
    print(i, fac, "done")
