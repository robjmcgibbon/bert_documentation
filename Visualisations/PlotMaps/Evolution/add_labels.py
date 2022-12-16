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

def add_label(args):

  z, type, input, output = args

  img = pl.imread(input)

  fig, ax = pl.subplots(figsize=(6,6))

  ax.imshow(img)
  ax.text(50, 50, f"$z = {z:5.2f}$, {labels[type]}", color="w")

  ax.axis("off")
  pl.tight_layout(pad=0)
  pl.savefig(output, dpi=300)
  fig.clear()
  pl.close(fig)

  return output

if __name__ == "__main__":

  mp.set_start_method("forkserver")

  argparser = argparse.ArgumentParser()
  argparser.add_argument("inputfolder")
  argparser.add_argument("outputfolder")
  argparser.add_argument("--zmax", "-z", type=float, default=15.)
  argparser.add_argument("--nframe", "-n", type=int, default=100)
  argparser.add_argument("--nproc", "-j", type=int, default=1)
  argparser.add_argument("--imin", "-i", type=int, default=-1)
  argparser.add_argument("--imax", "-I", type=int, default=-1)
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
      input = f"{args.inputfolder}/{type}_frame_{idx:04d}.png"
      output = f"{args.outputfolder}/{type}_frame_{idx:04d}.png"
      arglist.append((z, type, input, output))

  os.makedirs(args.outputfolder, exist_ok=True)

  pool = mp.Pool(args.nproc)
  for output in pool.imap_unordered(add_label, arglist):
    print(output)
