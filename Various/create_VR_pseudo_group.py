#!/usr/bin/env python3

"""
create_VR_pseudo_group.py

Script that can be used to create a pseudo-VR SOAP catalogue file that could be
used in conjunction with an early version of velociraptor-python to run the
usual pipeline on a SOAP catalogue.

The idea is quite simple: we just add some meta-data and virtual datasets to
the SOAP catalogue that make it possible to access the SOAP catalogue file as
if it was a VR catalogue file. Whenever a VR dataset is accessed, we link to
the corresponding SOAP dataset. This does not work for datasets that exist in
VR but not in SOAP, or that have a different meaning in SOAP (like velocity
dispersions and some metallicities).

While this script is no longer used (since velociraptor-python took a different
approach to support SOAP), it contains some useful code, e.g. code to generate
virtual datasets.

This script uses matching information from the vr_props.yml file found in this
folder. This file simply links a VR name to the corresponding SOAP dataset, and
the column in that dataset for multi-column datasets (which do not exist in VR).
"""

import h5py
import yaml
import os


def create_virtual_dset_all(
    source_file, source_file_name, dest_file, source_name, dest_name
):
    dset = source_file[source_name]
    shape = dset.shape
    sspace = dset.id.get_space()
    sspace.select_all()

    vspace = h5py.h5s.create_simple((shape[0],), (shape[0],))
    plist = h5py.h5p.create(h5py.h5p.DATASET_CREATE)
    plist.set_layout(h5py.h5d.VIRTUAL)
    plist.set_virtual(
        vspace, source_file_name.encode("utf-8"), source_name.encode("utf-8"), sspace
    )

    h5py.h5d.create(
        dest_file.id, dest_name.encode("utf-8"), dset.id.get_type(), vspace, plist
    ).close()
    return dest_file[dest_name]


def create_virtual_dset_column(
    source_file, source_file_name, dest_file, source_name, dest_name, column
):
    dset = source_file[source_name]
    shape = dset.shape
    sspace = dset.id.get_space()
    sspace.select_hyperslab((0, column), (shape[0], 1))

    vspace = h5py.h5s.create_simple((shape[0],), (shape[0],))
    plist = h5py.h5p.create(h5py.h5p.DATASET_CREATE)
    plist.set_layout(h5py.h5d.VIRTUAL)
    plist.set_virtual(
        vspace, source_file_name.encode("utf-8"), source_name.encode("utf-8"), sspace
    )

    h5py.h5d.create(
        dest_file.id, dest_name.encode("utf-8"), dset.id.get_type(), vspace, plist
    ).close()
    return dest_file[dest_name]


def copy_attributes(source_file, dest_file, source_name, dest_name):
    sdset = source_file[source_name]
    tdset = dest_file[dest_name]
    for attr in sdset.attrs:
        tdset.attrs[attr] = sdset.attrs[attr]


def add_pseudo_VR_group(SOAP_file, pseudo_VR_file, VR_props_file, boxsize):

    with open(VR_props_file, "r") as file:
        propdict = yaml.safe_load(file)

    source_file_name = os.path.basename(SOAP_file)
    with h5py.File(SOAP_file, "r") as source_file, h5py.File(
        pseudo_VR_file, "w"
    ) as dest_file:
        source_file.copy("SWIFT", dest_file)
        dest_file.create_group("PseudoVR")
        dest_file["PseudoVR"].attrs["Boxsize_in_comoving_Mpc"] = boxsize
        for prop in propdict:
            target = propdict[prop]["target"]
            if not target in source_file:
                print(target, "not found")
            else:
                newname = f"PseudoVR/{prop}"
                if "column" in propdict[prop]:
                    column = propdict[prop]["column"]
                    create_virtual_dset_column(
                        source_file,
                        source_file_name,
                        dest_file,
                        target,
                        newname,
                        column,
                    )
                else:
                    create_virtual_dset_all(
                        source_file, source_file_name, dest_file, target, newname
                    )
                copy_attributes(source_file, dest_file, target, newname)


if __name__ == "__main__":

    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("SOAP")
    argparser.add_argument("PseudoVR")
    argparser.add_argument("props")
    argparser.add_argument("--boxsize", "-b", type=float, default=1000.0)
    args = argparser.parse_args()

    add_pseudo_VR_group(args.SOAP, args.PseudoVR, args.props, args.boxsize)
