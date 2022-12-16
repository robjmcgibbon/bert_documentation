import numpy as np
import glob
import argparse
import multiprocessing as mp
import os

def convert_file(args):

  input, output = args

  data = np.load(input)
  newdata = {}
  for key in data.files:
    newdata[key] = data[key][:100,:100]

  np.savez_compressed(output, **newdata)

  return output

if __name__ == "__main__":

  mp.set_start_method("forkserver")

  argparser = argparse.ArgumentParser()
  argparser.add_argument("inputfolder")
  argparser.add_argument("outputfolder")
  argparser.add_argument("--nproc", "-j", type=int, default=1)
  args = argparser.parse_args()

  files = sorted(glob.glob(f"{args.inputfolder}/*.npz"))

  os.makedirs(args.outputfolder, exist_ok=True)

  arglist = [(file, f"{args.outputfolder}/{os.path.basename(file)}") for file in files]

  pool = mp.Pool(args.nproc)
  for file in pool.imap_unordered(convert_file, arglist):
    print(file)
