import os
import numpy as np
import multiprocessing as mp
import glob
import argparse
import yaml

def process_file(filename):
  data = np.load(filename)
  name = data.files[0]
  data = data[name]
  if name == "surfdens":
    dmean = data.mean()
    if dmean > 0.:
      data /= dmean
  dmin = data.min()
  dmax = data.max()
  return filename, name, dmin, dmax

if __name__ == "__main__":

  # mp.set_start_method("forkserver")

  argparser = argparse.ArgumentParser()
  argparser.add_argument("folder")
  argparser.add_argument("output")
  argparser.add_argument("--nproc", "-j", type=int, default=1)
  args = argparser.parse_args()

  files = []
  for dirname in os.listdir(args.folder):
      if 'snapshot_' in dirname:
          files += glob.glob(f'{args.folder}/{dirname}/*.npz')

  pool = mp.Pool(args.nproc)
  data = {}
  for file, name, dmin, dmax in pool.imap_unordered(process_file, files):
    print(file)
    data[file] = {"quantity": name, "min": f"{dmin:.9e}", "max": f"{dmax:.9e}"}
    print(file, data[file])

  with open(args.output, "w") as handle:
    handle.write(yaml.safe_dump(data))
