#!/usr/bin/env python3

"""
get_storage_sizes.py

Get the size (in bytes) of all the datasets in an HDF5 file and write them to
a `.yml` file. Returns the actual size on disk, including the impact of lossy
and lossless compression.
"""

import h5py
import argparse
import time
import yaml


class H5printer:
    """
    Functor (class that acts as a function) used to access the HDF5 file.
    """

    def __init__(self):
        """
        Constructor. Create an empty results dictionary.
        """
        self.objects = {}

    def __call__(self, name, h5obj):
        """
        Functor function, i.e. what gets called when you use () on an object
        of this class. Conforms to the h5py.Group.visititems() function
        signature.

        Parameters:
         - name: Full path to a group/dataset in the HDF5 file
                  e.g. SO/200_crit/TotalMass
         - h5obj: HDF5 file object pointed at by this path
                   e.g. SO/200_crit/TotalMass --> h5py.Dataset
                        SO/200_crit --> h5py.Group
        """
        if isinstance(h5obj, h5py.Dataset):
            # get the actual storage size (h5py.Dataset.id.get_storage_size()),
            # but only for dataset objects
            size = h5obj.id.get_storage_size()
            self.objects[name] = size


if __name__ == "__main__":
    """
    Main script entry point.
    """

    argparser = argparse.ArgumentParser()
    argparser.add_argument("input", help="Input HDF5 file.")
    argparser.add_argument(
        "output",
        help="Output file. Will be in YAML format, .yml extension recommended.",
    )
    args = argparser.parse_args()

    tic = time.time()
    h5print = H5printer()
    with h5py.File(args.input, "r") as ifile:
        ifile.visititems(h5print)
    toc = time.time()
    print(f"Reading dataset sizes took {1000.*(toc-tic):.2f} ms.")

    with open(args.output, "w") as handle:
        yaml.safe_dump(h5print.objects, handle)
