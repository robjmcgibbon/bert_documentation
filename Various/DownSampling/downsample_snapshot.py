import numpy as np
import h5py
import argparse
import multiprocessing as mp
import glob
import os
import shutil
from create_virtual_snapshot import create_virtual_snapshot
import re

# names of particles types
# used for soft links in file
particle_names = [
    "GasParticles",
    "DMParticles",
    "DMBackgroundParticles",
    "SinkParticles",
    "StarsParticles",
    "BHParticles",
    "NeutrinoParticles",
]

# dictionary of particle data transforms
# this dictionary has a double purpose:
# 1. provide a list of all quantities we want to keep in the downsampled snapshot
# 2. provide a transform for each quantity, or None for no transform
# a transform is a function (or lambda) that takes the data and the
# subsampling fraction as an input and returns the transformed data
transforms = {
    "PartType0": {
        "ComptonYParameters": None,
        "Coordinates": None,
        "Masses": lambda x, frac: x / frac,
        "Velocities": None,
    },
    "PartType1": {
        "Coordinates": None,
        "Masses": lambda x, frac: x / frac,
        "Velocities": None,
    },
    "PartType4": {
        "Coordinates": None,
        "Masses": lambda x, frac: x / frac,
        "Velocities": None,
    },
    "PartType5": {
        "Coordinates": None,
        "DynamicalMasses": None,
        "SubgridMasses": None,
        "Velocities": None,
    },
    "PartType6": {
        "Coordinates": None,
        "Masses": lambda x, frac: x / frac,
        "SampledSpeeds": None,
        "Velocities": None,
        "Weights": None,
    },
}


def create_dataset_like(input_dset, output_group, dset_name, dsize):
    """
    Create a new dataset with the given name in the given group
    that uses the same filters as the given input dataset.
    """

    cplist = input_dset.id.get_create_plist().copy()
    dtype = input_dset.id.get_type()
    old_shape = input_dset.shape
    chunksize = input_dset.chunks
    if chunksize is not None:
        # make sure the chunksize is not larger than the data
        if len(chunksize) == 1:
            chunk = (min(chunksize[0], dsize),)
        else:
            chunk = (min(chunksize[0], dsize), chunksize[1])
        cplist.set_chunk(chunk)
    if len(old_shape) == 1:
        dshape = (dsize,)
    else:
        dshape = (dsize, old_shape[1])
    # create the new dataset with the right filters using the low level API
    space = h5py.h5s.create_simple(dshape, dshape)
    h5py.h5d.create(
        output_group.id, dset_name.encode("utf-8"), dtype, space, cplist, None
    ).close()
    space.close()


class H5copier:
    """
    Auxiliary class used to copy data from one HDF5 file to another.
    Virtual datasets are converted into real datasets in the process.
    """

    def __init__(self, ifile, ofile):
        super().__init__()
        self.ifile = ifile
        self.ofile = ofile
        self.virtual_dsets = []

    def __call__(self, name, h5obj):
        """
        Function that can be passed on to h5py.visititems()
        to copy all data in an HDF5 file.
        """

        # Figure out what type of object we are dealing with
        if isinstance(h5obj, h5py.Group):
            type = "group"
        elif isinstance(h5obj, h5py.Dataset):
            if h5obj.is_virtual:
                type = "virtual_dataset"
            else:
                type = "dataset"
        else:
            raise RuntimeError(f"Unknown HDF5 object type: {name}")

        # Now treat the object accordingly
        if type == "group":
            # Groups and their attributes are simply copied
            self.ofile.create_group(name)
            for attr in h5obj.attrs:
                self.ofile[name].attrs[attr] = h5obj.attrs[attr]
        elif type == "dataset":
            # Normal datasets are also simply copied
            self.ifile.copy(name, self.ofile, name=name)
        elif type == "virtual_dataset":
            self.virtual_dsets.append(name)
            """
            # Virtual datasets are copied properly,
            # i.e. we create a new dataset that is not virtual
            # and contains the same data
            data = h5obj[:]
            sources = h5obj.virtual_sources()
            with h5py.File(sources[0].file_name) as handle:
                old_dset = handle[name]
                create_dataset_like(old_dset, ofile, name, h5obj.shape[0])
            self.ofile[name][:] = data
            for attr in h5obj.attrs:
                self.ofile[name].attrs[attr] = h5obj.attrs[attr]
            """


def copy_virtual_dset(args):
    """
    Copy the contents of a virtual dataset into a separate file as a real dataset.

    This function takes a tuple of 3 arguments:
    1. Name of the input file (read-only)
    2. Name of the output file (is overwritten if it exists)
    3. Name of the virtual dataset to copy.
    The dataset is written as a new dataset with the name "data".

    This function returns the name of the dataset. The return value
    is supposed to be used to display progress.
    """

    input_file, output_file, dset_name = args

    with h5py.File(input_file, "r") as ifile, h5py.File(output_file, "w") as ofile:
        dset = ifile[dset_name]
        data = dset[:]
        # a virtual dataset does not have filters
        # open the first real underlying dataset to read those
        # and set up the output dataset
        sources = dset.virtual_sources()
        with h5py.File(sources[0].file_name, "r") as handle:
            old_dset = handle[dset_name]
            create_dataset_like(old_dset, ofile, "data", dset.shape[0])
        # copy the data and attributes
        ofile["data"][:] = data
        for attr in dset.attrs:
            ofile["data"].attrs[attr] = dset.attrs[attr]

    return dset_name


def downsample_file(args):
    """
    Downsample a single snapshot file

    This function takes a tuple of 4 arguments:
    1. seed: The seed for the random number generator.
             To guarantee unbiased sampling, this should be
             different for each file.
    2. input_file: input snapshot file (read-only)
    3. output_file: output downsampled snapshot file (is overwritten if it exists)
    4. fraction: downsampling fraction

    This function returns the name of the input file. The return argument is meant
    to be used to display progress.
    """

    seed, input_file, output_file, fraction = args

    # make the downsampling procedure reproducible
    # note that the seed should be set to a different value for each task
    np.random.seed(seed)
    with h5py.File(input_file, "r") as ifile, h5py.File(output_file, "w") as ofile:
        # copy all groups except the particles
        # these groups require no or very small changes
        for key in ifile.keys():
            # skip particle groups and their softlinks
            if not key.startswith("PartType") and not key.endswith("Particles"):
                ifile.copy(key, ofile)

        # get the number of particles
        npart = ifile["Header"].attrs["NumPart_ThisFile"][:]
        # loop over particle types
        for ipart, partname in enumerate(particle_names):
            groupname = f"PartType{ipart}"
            # skip groups that are not present or that we do not want to keep
            if (not groupname in transforms) or (not groupname in ifile):
                continue
            oldgroup = ifile[groupname]
            newgroup = ofile.create_group(groupname)
            for attr in oldgroup.attrs:
                newgroup.attrs[attr] = oldgroup.attrs[attr]
            # keep all BHs, subsample the rest
            pfraction = 1.0 if partname == "BHParticles" else fraction
            # create a mask for this particle type
            mask = np.random.random(npart[ipart]) < pfraction
            npart[ipart] = mask.sum()
            # now mask out all the datasets
            for dset in oldgroup.keys():
                if not dset in transforms[groupname]:
                    continue
                # we need to copy the data type and creation property list
                # from the original dataset, since these contain the
                # lossy and lossless compression filters
                old_dset = oldgroup[dset]
                create_dataset_like(old_dset, newgroup, dset, npart[ipart])
                data = old_dset[:][mask]
                # apply the transform, if required
                transform = transforms[groupname][dset]
                if transform is not None:
                    data = transform(data, pfraction)
                newgroup[dset][:] = data
                # and copy the attributes
                for attr in oldgroup[dset].attrs:
                    newgroup[dset].attrs[attr] = oldgroup[dset].attrs[attr]

            # update the cell metadata
            # we have removed particles from cells, so we need to update the offsets and counts
            file_index = ofile["Header"].attrs["ThisFile"][0]
            cell_mask = ofile[f"Cells/Files/{groupname}"][:] == file_index
            offsets = ofile[f"Cells/OffsetsInFile/{groupname}"][:][cell_mask]
            counts = ofile[f"Cells/Counts/{groupname}"][:][cell_mask]
            newcounts = np.zeros(counts.shape, dtype=counts.dtype)
            for icell, (ofs, cnt) in enumerate(zip(offsets, counts)):
                newcounts[icell] = mask[ofs : ofs + cnt].sum()
            newoffsets = np.zeros(offsets.shape, dtype=offsets.dtype)
            ofssort = np.argsort(offsets)
            newoffsets[ofssort] = newcounts[ofssort].cumsum() - newcounts[ofssort]
            offsets = ofile[f"Cells/OffsetsInFile/{groupname}"][:]
            counts = ofile[f"Cells/Counts/{groupname}"][:]
            offsets[cell_mask] = newoffsets
            counts[cell_mask] = newcounts
            ofile[f"Cells/OffsetsInFile/{groupname}"][:] = offsets
            ofile[f"Cells/Counts/{groupname}"][:] = counts

            # finally: create the soft links for the particle groups
            ofile[partname] = h5py.SoftLink(groupname)

        ofile["Header"].attrs["NumPart_ThisFile"] = npart

    return input_file


if __name__ == "__main__":

    # use a multiprocessing spawn method that copies a minimal amount of memory
    mp.set_start_method("forkserver")

    argparser = argparse.ArgumentParser()
    argparser.add_argument("input")
    argparser.add_argument("output")
    argparser.add_argument("fraction", type=float)
    argparser.add_argument("seed", type=int)
    argparser.add_argument("--nproc", "-j", type=int, default=32)
    args = argparser.parse_args()

    files = sorted(glob.glob(f"{args.input}.*.hdf5"))
    if len(files) == 0:
        files = [f"{args.input}.hdf5"]
    print(f"Will downsample {len(files)} file(s).")

    output_prefix = args.output.removesuffix(".hdf5")
    temp_folder = f"{output_prefix}_temporary_files"

    print(f"Creating temporary output folder {temp_folder}")
    os.makedirs(temp_folder, exist_ok=True)

    print(f"Setting up downsampling task(s)")
    file_tasks = []
    for ifile, file in enumerate(files):
        suffix = file.removeprefix(args.input)
        file_tasks.append(
            (
                args.seed + ifile,
                file,
                f"{temp_folder}/{output_prefix}{suffix}",
                args.fraction,
            )
        )

    nproc = min(args.nproc, len(files))
    print(f"Will run {nproc} tasks in parallel")
    pool = mp.Pool(nproc)
    count = 0
    totcount = len(file_tasks)
    print(f"[{count:04d}/{totcount:04d}] (starting)".ljust(80), end="\r")
    for file in pool.imap_unordered(downsample_file, file_tasks):
        count += 1
        print(f"[{count:04d}/{totcount:04d}] {file}".ljust(80), end="\r")
    print("\nDone.")

    print("Gathering new cell meta-data and particle numbers")
    counts = {}
    offsets = {}
    npart_total = None
    count = 0
    totcount = len(file_tasks)
    for _, _, output_file, _ in file_tasks:
        count += 1
        print(f"[{count:04d}/{totcount:04d}] {output_file}".ljust(80), end="\r")
        with h5py.File(output_file, "r") as handle:
            npart_thisfile = handle["Header"].attrs["NumPart_ThisFile"][:]
            if npart_total is None:
                npart_total = np.array(npart_thisfile)
            else:
                npart_total += npart_thisfile
            for ipart in range(len(npart_thisfile)):
                partname = f"PartType{ipart}"
                if not partname in handle["Cells/OffsetsInFile"]:
                    continue
                offsets_thisfile = handle[f"Cells/OffsetsInFile/{partname}"][:]
                counts_thisfile = handle[f"Cells/Counts/{partname}"][:]
                if not partname in offsets:
                    offsets[partname] = offsets_thisfile
                    counts[partname] = counts_thisfile
                else:
                    file_index = handle["Header"].attrs["ThisFile"][0]
                    cell_mask = handle[f"Cells/Files/{partname}"][:] == file_index
                    offsets[partname][cell_mask] = offsets_thisfile[cell_mask]
                    counts[partname][cell_mask] = counts_thisfile[cell_mask]
    print("\nDone.")

    print("Setting new cell meta-data")
    count = 0
    totcount = len(file_tasks)
    for _, _, output_file, _ in file_tasks:
        count += 1
        print(f"[{count:04d}/{totcount:04d}] {output_file}".ljust(80), end="\r")
        with h5py.File(output_file, "r+") as handle:
            ntot = handle["Header"].attrs["NumPart_Total"]
            handle["Header"].attrs["NumPart_Total"] = npart_total.astype(ntot.dtype)
            ntot_high = handle["Header"].attrs["NumPart_Total_HighWord"]
            handle["Header"].attrs["NumPart_Total_HighWord"] = np.zeros(
                ntot_high.shape, dtype=ntot_high.dtype
            )
            for ipart in range(len(npart_thisfile)):
                partname = f"PartType{ipart}"
                if not partname in handle["Cells/OffsetsInFile"]:
                    continue
                handle[f"Cells/OffsetsInFile/{partname}"][:] = offsets[partname][:]
                handle[f"Cells/Counts/{partname}"][:] = counts[partname][:]
    print("\nDone.")

    print("Generating new virtual snapshot")
    create_virtual_snapshot(file_tasks[0][2], force=True, verbose=True)

    print("Copying virtual snapshot into a single real snapshot")
    print("Copying over real datasets and structure")
    with h5py.File(f"{temp_folder}/{output_prefix}.hdf5", "r") as ifile, h5py.File(
        f"{output_prefix}.hdf5", "w"
    ) as ofile:
        h5copy = H5copier(ifile, ofile)
        ifile.visititems(h5copy)
        for ipart, part_name in enumerate(particle_names):
            group_name = f"PartType{ipart}"
            if group_name in ofile:
                ofile[part_name] = h5py.SoftLink(group_name)

    print("Setting up tasks to copy virtual datasets")
    virtual_dsets = []
    for vdset in h5copy.virtual_dsets:
        vdname = vdset.replace("/", "_")
        virtual_dsets.append(
            (
                f"{temp_folder}/{output_prefix}.hdf5",
                f"{temp_folder}/{output_prefix}_{vdname}.hdf5",
                vdset,
            )
        )

    nproc = min(args.nproc, len(virtual_dsets))
    print(f"Will copy virtual datasets using {nproc} tasks in parallel")
    pool = mp.Pool(nproc)
    count = 0
    totcount = len(virtual_dsets)
    print(f"[{count:04d}/{totcount:04d}] (starting)".ljust(80), end="\r")
    for dset in pool.imap_unordered(copy_virtual_dset, virtual_dsets):
        count += 1
        print(f"[{count:04d}/{totcount:04d}] {dset}".ljust(80), end="\r")
    print("\nDone.")

    print("Copying over virtual datasets to output file")
    with h5py.File(f"{output_prefix}.hdf5", "r+") as ofile:
        for _, tfilename, dset_name in virtual_dsets:
            with h5py.File(tfilename, "r") as tfile:
                tfile.copy("data", ofile, name=dset_name)
    print("Done.")

    print(f"Removing temporary folder {temp_folder}")
    shutil.rmtree(temp_folder)
    print("Done")
