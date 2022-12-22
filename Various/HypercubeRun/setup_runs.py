#!/usr/bin/env python3

"""
setup_runs.py

Set up the working directories for a set of hypercube runs.

Usage:
  python3 setup_runs.py YAML1 [YAML2...] COPY LINK TEMPLATE OUTPUT
where:
 - YAML1... are the `.yml` files created by `create_hypercube.py`.
 - COPY is a list of files that need to be copied into each working directory
   (see `copy_files.txt` for an example)
 - LINK is a list of files that need to be soft-linked into each working
   directory (see `link_files.txt` for an example)
 - TEMPLATE is a list of files that need to be copied with some substitutions
   (see `template_files.txt` for an example). Currently the following
   substitutions are performed: `@NAME@` is replaced with
   `L25-HyperCube-Pressure-BASE`, where `BASE` is the original name of the run
   `.yml` file without the `.yml` extension (and without any directory path),
   `@PARAMS@` is replaced with the base name of the `.yml` file (including
   the extension, but without any directory path).
 - OUTPUT is the name of the file where the list of working directories will
   be stored. This list can then be used by other scripts to manage the runs.

The script will also copy `submit_VR.slurm.template` into each working
directory 3 times and substitute `@SNAP@` with a four digit snapshot number,
for numbers 490, 623, 2729.
"""

import argparse
import os
import shutil

if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument("yml", nargs="+")
    argparser.add_argument("copy")
    argparser.add_argument("link")
    argparser.add_argument("template")
    argparser.add_argument("output")
    args = argparser.parse_args()

    ymllist = [os.path.abspath(yml) for yml in args.yml]

    with open(args.copy, "r") as handle:
        copylist = [os.path.abspath(line.strip()) for line in handle.readlines()]

    with open(args.link, "r") as handle:
        linklist = [os.path.abspath(line.strip()) for line in handle.readlines()]

    with open(args.template, "r") as handle:
        templist = [os.path.abspath(line.strip()) for line in handle.readlines()]

    outputfile = os.path.abspath(args.output)

    runs = []
    for ymlfile in ymllist:
        _, yml = os.path.split(ymlfile)
        base = yml.removesuffix(".yml")
        wdir = f"{os.getcwd()}/wdir_{base}"

        substitutions = {
            "@NAME@": f"L25-HyperCube-Pressure-{base}",
            "@PARAMS@": yml,
        }

        if os.path.exists(wdir):
            shutil.rmtree(wdir)
        os.makedirs(wdir)

        runs.append(wdir)

        shutil.copy(ymlfile, f"{wdir}/{yml}")
        for cfilepath in copylist:
            _, cfile = os.path.split(cfilepath)
            shutil.copy(cfilepath, f"{wdir}/{cfile}")
        for lfilepath in linklist:
            _, lfile = os.path.split(lfilepath)
            os.symlink(lfilepath, f"{wdir}/{lfile}")
        for tfilepath in templist:
            _, tfile = os.path.split(tfilepath)
            tbase = tfile.removesuffix(".template")
            with open(tfilepath, "r") as ifile, open(f"{wdir}/{tbase}", "w") as ofile:
                temp = ifile.read()
                for key, val in substitutions.items():
                    temp = temp.replace(key, val)
                ofile.write(temp)

        for snap in [490, 623, 2729]:
            VRsubs = dict(substitutions)
            VRsubs["@SNAP@"] = f"{snap:04d}"
            with open("submit_VR.slurm.template", "r") as ifile, open(
                f"{wdir}/submit_VR_{snap:04d}.slurm", "w"
            ) as ofile:
                temp = ifile.read()
                for key, val in VRsubs.items():
                    temp = temp.replace(key, val)
                ofile.write(temp)

    with open(outputfile, "w") as handle:
        for run in runs:
            handle.write(f"{run}\n")
