#!/usr/bin/env python3

"""
snapshot_contents.py

Print all the datasets in an HDF5 file.
Mostly useful to check the contents of a SWIFT snapshot file.

Usage:
  python3 snapshot_contents.py INPUT
where INPUT is the name of the snapshot file.
"""

import h5py
import argparse


class H5ls:
    """
    Functor (class that acts as a function) used to retrieve the snapshot
    contents. Could also be a function in this case.
    """

    def __call__(self, name, h5obj):
        """
        Function that is called when () is used on an object of this class.

        Conforms to the h5py.Group.visititems() expected function signature, i.e.
         - name: Path of a dataset or group in the HDF5 file,
                  e.g. PartType0/Coordinates
         - h5obj: Underlying h5py object,
                   e.g. PartType0/Coordinates --> h5py.Dataset
                        PartType0 --> h5py.Group
        """
        if isinstance(h5obj, h5py.Dataset):
            # Print the path, but only for dataset objects
            print(name)


if __name__ == "__main__":
    """
    Main entry point.
    """

    argparser = argparse.ArgumentParser()
    argparser.add_argument("input")
    args = argparser.parse_args()

    with h5py.File(args.input, "r") as ifile:
        h5ls = H5ls()
        ifile.visititems(h5ls)
