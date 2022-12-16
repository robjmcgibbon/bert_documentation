import numpy as np
import yaml
import argparse
import re

if __name__ == "__main__":

  argparser = argparse.ArgumentParser()
  argparser.add_argument("limitsfile")
  argparser.add_argument("redshiftfile")
  argparser.add_argument("outputfile")
  args = argparser.parse_args()

  with open(args.limitsfile, "r") as handle:
    limits = yaml.safe_load(handle.read())

  zs = np.loadtxt(args.redshiftfile)

  for file in limits:
    idx = int(re.search("00\d\d", file)[0])
    limits[file]["redshift"] = f"{zs[idx]:.2f}"

  with open(args.outputfile, "w") as handle:
    handle.write(yaml.safe_dump(limits))
