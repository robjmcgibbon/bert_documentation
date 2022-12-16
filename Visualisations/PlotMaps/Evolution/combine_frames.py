import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as pl
import multiprocessing as mp
import argparse
import os

pl.rcParams["text.usetex"] = True

labels = {
  "gas": "Gas surface density and temperature",
  "dm": "Dark matter surface density",
  "star": "Stellar surface density",
  "xray": "ROSAT X-ray luminosity",
}

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

def combine_frames(args):

  z, type, input_large, input_small, output, selection, boxsize = args

  img_large = pl.imread(input_large)
  img_small = pl.imread(input_small)
  logo = pl.imread("FLAMINGO_thumbnailer.png")

  boxsize_large = boxsize
  boxsize_small = (selection[1]-selection[0])*boxsize

  fig, ax = pl.subplots(1, 2, figsize=(12,6))

  ax[0].imshow(img_large, extent=[0., 1., 0., 1.])
  ax[0].text(0.05, 0.95, f"$z = {z:5.2f}$, {labels[type]}", color="w")
  ax[0].plot([selection[0], selection[0], selection[1], selection[1], selection[0]],
             [selection[2], selection[3], selection[3], selection[2], selection[2]], "-", color="w",
             linewidth=0.4)
  ax[0].plot([selection[1], 1.], [selection[2], 0.], "-", color="w", linewidth=0.4)
  ax[0].plot([selection[1], 1.], [selection[3], 1.], "-", color="w", linewidth=0.4)

  label_fraction = get_label_fraction(boxsize_large)
  scale_label = f"{label_fraction*boxsize_large:.0f} Mpc"
  ax[0].plot(
        [0.05, 0.05 + label_fraction],
        [0.05, 0.05],
        "w-",
    )
  ax[0].text(0.05, 0.07, scale_label, color="w")

  ax[1].imshow(img_small, extent=[0., 1., 0., 1.])
  ax[1].plot([0., 0., 1., 1., 0.], [0., 1., 1., 0., 0.], "-", color="w")

  label_fraction = get_label_fraction(boxsize_small)
  scale_label = f"{label_fraction*boxsize_small:.0f} Mpc"
  ax[1].plot(
        [0.05, 0.05 + label_fraction],
        [0.05, 0.05],
        "w-",
    )
  ax[1].text(0.05, 0.07, scale_label, color="w")
  ax[1].text(0.7, 0.06, "FLAMINGO", color="w")
  ax[1].text(0.7, 0.03, "Virgo Consortium", color="w")

  ax[0].axis("off")
  ax[1].axis("off")
  pl.tight_layout(pad=0)
  ax = fig. add_axes([0.92,0.02,0.1,0.1])
  ax.imshow(logo)
  ax.axis("off")
  pl.savefig(output, dpi=300)
  fig.clear()
  pl.close(fig)

  return output

if __name__ == "__main__":

  mp.set_start_method("forkserver")

  argparser = argparse.ArgumentParser()
  argparser.add_argument("inputfolderlarge")
  argparser.add_argument("inputfoldersmall")
  argparser.add_argument("outputfolder")
  argparser.add_argument("--selection", "-s", type=float, nargs=4, default=[0.4375, 0.5625, 0.4375, 0.5625])
  argparser.add_argument("--zmax", "-z", type=float, default=15.)
  argparser.add_argument("--nframe", "-n", type=int, default=100)
  argparser.add_argument("--nproc", "-j", type=int, default=1)
  argparser.add_argument("--imin", "-i", type=int, default=-1)
  argparser.add_argument("--imax", "-I", type=int, default=-1)
  argparser.add_argument("--boxsizeMpc", "-b", type=float, default=1000.)
  args = argparser.parse_args()

  a_range = np.linspace(1./(1.+args.zmax), 1., args.nframe)
  z_range = 1./a_range - 1.

  arglist = []
  for idx, z in enumerate(z_range):
    if args.imin >= 0 and idx < args.imin:
      continue
    if args.imax >= 0 and idx >= args.imax:
      continue
    for type in ["gas", "dm", "star", "xray"]:
      input_large = f"{args.inputfolderlarge}/{type}_frame_{idx:04d}.png"
      input_small = f"{args.inputfoldersmall}/{type}_frame_{idx:04d}.png"
      output = f"{args.outputfolder}/{type}_frame_{idx:04d}.png"
      arglist.append((z, type, input_large, input_small, output, args.selection, args.boxsizeMpc))

  os.makedirs(args.outputfolder, exist_ok=True)

  pool = mp.Pool(args.nproc)
  for output in pool.imap_unordered(combine_frames, arglist):
    print(output)
