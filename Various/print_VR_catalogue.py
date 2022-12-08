import h5py
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("input")
argparser.add_argument("output")
args = argparser.parse_args()

with h5py.File(args.input, "r") as ifile, open(args.output, "w") as ofile:
  for key in ifile.keys():
    ofile.write(f"{key}\n")
