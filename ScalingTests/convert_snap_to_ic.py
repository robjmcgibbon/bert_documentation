#!/usr/bin/env python3

"""
Convert a snapshot file into an IC.
Usage:
  ./convert_snap_to_ic.py input output [--replicate factor] [--compression]

where 'input' is the path to a valid SWIFT snapshot file and 'output' is the
name of a newly created SWIFT IC file.
The following optional arguments activate extra functionality:
 --replicate     Multiply the box size with the given 'factor' and fill it up
                 with copies of the original particles with appropriately
                 shifted particles. The total number of particles will be a
                 factor 'factor'^3 larger than in the original snapshot.
 --compression   Compress the datasets in the new IC file using aggressive,
                 lossless GZIP compression. This leads to a much smaller IC
                 file, but has a very significant impact on the runtime of the
                 script.

Note that high replication factors can lead to very large files. On Lustre
file systems (such as /cosma7, /cosma8, /snap7 and /snap8), appropriate file
striping needs to be set for these large files to not overflow individual
OSTs. The recommended strategy is to allow striping to all available OSTs, by
setting
  lfs setstripe -c -1 output
where 'output' is the same output file name as used for this script. Note that
this command needs to be executed before the file is created.
You can check the striping of a file after it was created with
  lfs getstripe FILENAME

To start a SWIFT simulation using the newly created IC, you need to make sure
the scale factor parameters in various parameter files are set to appropriate
values. SWIFT will crash if these numbers are not compatible with the scale
factor in the IC file, which is the same as in the snapshot file used to
generate the IC. To facilitate this, the script outputs the scale factor as
encountered in the snapshot file. The following is a non-exhaustive list of
parameters that need to be changed accordingly:
 - Cosmology:a_begin
 - FOF:scale_factor_first
 - Snapshots:scale_factor_first
 - Statistics:scale_factor_first
If you use any kind of output list for the simulation, you also need to make
sure all scale factor entries smaller than the current IC scale factor are
removed, since they will also lead to SWIFT crashes.

Since the IC will contain all types of particles and uses the snapshot
convention for properties where this matters, the following parameters values
need to be used in the InitialConditions parameter block:
  cleanup_h_factors: 0
  cleanup_smoothing_lengths: 0
  cleanup_velocity_factors: 0
  generate_gas_in_ics: 0
  periodic: 1
  remap_ids: 0

Note that the simulation needs to be started as if it was run from real ICs,
i.e. you cannot use a "--restart" argument. This also means that some variables
will be initialised as if the simulation was started from scratch; this is
not a valid or recommended restart mechanism and is only intended for
performance testing!
"""

import numpy as np
import h5py
import argparse
import time

# timed output messages
mastertic = time.time()


def print_message(*m):
    """
    print() wrapper that adds a time stamp to the beginning of the message.
    """
    toc = time.time()
    message = f"[{toc-mastertic:10.2f}]"
    print(message, *m)


# parse command line arguments
argparser = argparse.ArgumentParser(
    "Convert a snapshot to an IC by copying relevant datasets."
)
argparser.add_argument("input", action="store", help="Input file.")
argparser.add_argument("output", action="store", help="Output file.")
argparser.add_argument(
    "--replicate", action="store", type=int, default=1, help="Replication factor"
)
argparser.add_argument(
    "--compression", action="store_true", help="Compress HDF5 datasets?"
)
args = argparser.parse_args()

# List of datasets that should be copied over from the snapshot file into the
# new IC file.
# This is a dictionary, with each entry corresponding to a particle group.
# The value for each entry is a list of tuples, with the first element in the
# tuple the name of the dataset in the IC file and the second argument its name
# in the snapshot file. This is necessary because some datasets have different
# names in ICs and in snapshots (e.g. "InternalEnergy" in the IC file vs
# "InternalEnergies" in the snapshot file).
# It is recommended to only include required datasets to keep the IC file as
# small as possible.
lists = {
    "PartType0": [
        ("Coordinates", "Coordinates"),
        ("Velocities", "Velocities"),
        ("Masses", "Masses"),
        ("SmoothingLength", "SmoothingLengths"),
        ("InternalEnergy", "InternalEnergies"),
        ("ParticleIDs", "ParticleIDs"),
        ("Density", "Densities"),
        ("ElementAbundance", "ElementMassFractions"),
        ("Metallicity", "MetalMassFractions"),
        ("IronMassFracFromSNIa", "IronMassFractionsFromSNIa"),
    ],
    "PartType1": [
        ("Coordinates", "Coordinates"),
        ("Velocities", "Velocities"),
        ("Masses", "Masses"),
        ("ParticleIDs", "ParticleIDs"),
    ],
    "PartType4": [
        ("Coordinates", "Coordinates"),
        ("Velocities", "Velocities"),
        ("Masses", "Masses"),
        ("ParticleIDs", "ParticleIDs"),
        ("SmoothingLength", "SmoothingLengths"),
        ("StellarFormationTime", "BirthScaleFactors"),
        ("BirthDensities", "BirthDensities"),
        ("BirthTemperatures", "BirthTemperatures"),
    ],
    "PartType5": [
        ("Coordinates", "Coordinates"),
        ("Velocities", "Velocities"),
        ("Masses", "DynamicalMasses"),
        ("ParticleIDs", "ParticleIDs"),
        ("SmoothingLength", "SmoothingLengths"),
        ("EnergyReservoir", "EnergyReservoirs"),
        ("SubgridMasses", "SubgridMasses"),
    ],
}

numtile = args.replicate**3
xfac = args.replicate**2
yfac = args.replicate
numshift = args.replicate
print_message(
    "numtile: {0}, xfac: {1}, yfac: {2}, numshift: {3}".format(
        numtile, xfac, yfac, numshift
    )
)

# open both files
with h5py.File(args.input, "r") as ifile, h5py.File(args.output, "w") as ofile:

    # copy all non-particle groups
    # omit the cell meta-data
    # this is a "deep" copy, i.e. all underlying datasets and attributes are
    # automatically copied as well
    # the data is copied in its binary file format, so there is minimal overhead
    for group in ifile.keys():
        if (not group.startswith("PartType")) and (not group == "Cells"):
            ifile.copy(group, ofile)

    # get the box size
    # replicate the header information, if required
    box = ifile["/Header"].attrs["BoxSize"]
    a = ifile["/Header"].attrs["Scale-factor"][0]
    print_message(f"Scale factor: {a}")
    if args.replicate > 1:
        ofile["/Header"].attrs["BoxSize"] = numshift * box
        ofile["/Header"].attrs["NumPart_ThisFile"] = (
            numtile * ifile["/Header"].attrs["NumPart_ThisFile"]
        )
        # deal with the annoying Gadget-2 way of storing the particle numbers
        npart_total = ofile["/Header"].attrs["NumPart_ThisFile"].astype(np.int64)
        npart_total_low = npart_total.astype(np.int32)
        npart_total_high = (npart_total >> 32).astype(np.int32)
        ofile["/Header"].attrs["NumPart_Total"] = npart_total_low
        ofile["/Header"].attrs["NumPart_Total_HighWord"] = npart_total_high

    # flush the file and read back the particle numbers
    # this is a useful check, since lots of subtle things can go wrong with the
    # high-word thingy and have done so in the past
    # since SWIFT reads these attributes to figure out how many particles there
    # are, it is really important to get these numbers right
    ofile.flush()
    print_message(f"Particle numbers after copying and replicating meta-data:")
    print_message(f"NumPart_ThisFile: {ofile['/Header'].attrs['NumPart_ThisFile']}")
    print_message(f"NumPart_Total: {ofile['/Header'].attrs['NumPart_Total']}")
    print_message(
        f"NumPart_Total_HighWord: {ofile['/Header'].attrs['NumPart_Total_HighWord']}"
    )
    npart_total_low = ofile["/Header"].attrs["NumPart_Total"].astype(np.int64)
    npart_total_high = ofile["/Header"].attrs["NumPart_Total_HighWord"].astype(np.int64)
    npart_total_ref = npart_total_low + (npart_total_high << 32)
    print_message(f"NumPart_Total sum: {npart_total_ref}")
    assert (npart_total_ref == npart_total).all()

    # now create the particle groups
    # we regenerate particle IDs for all types, starting from 1
    id_ofs = 1
    for pname in lists.keys():
        print_message(f"Reading {pname} group")
        # skip particle types that do not exist
        if not pname in ifile:
            print_message(f"{pname} not present in snapshot file, skipping")
            continue
        group = ifile[pname]
        newgroup = ofile.create_group(pname)
        # loop over the datasets we want to copy over for this particle type
        for dset in lists[pname]:
            # sanity check
            assert dset[1] in group
            data = group[dset[1]][:]
            # determine the shape of the new dataset
            oldshape = data.shape
            if len(oldshape) == 2:
                newshape = (oldshape[0] * numtile, oldshape[1])
            else:
                newshape = (oldshape[0] * numtile,)
            print_message(f"{dset[0]}: old shape: {oldshape} -> new shape: {newshape}")
            # create the new dataset (empty)
            # we do this because replicating the data and then writing it immediately
            # requires too much memory for large replication factors
            # instead, we create an empty dataset with the right shape and then write
            # the individual replications one at a time
            if args.compression:
                newds = newgroup.create_dataset(
                    dset[0],
                    shape=newshape,
                    dtype=data.dtype,
                    compression="gzip",
                    compression_opts=9,
                )
            else:
                newds = newgroup.create_dataset(
                    dset[0], shape=newshape, dtype=data.dtype
                )
            # loop over the replications
            for xshift in range(numshift):
                # be verbose. This was mainly added because SSH times out if there is
                # no stdout/stderr activity for too long, making the script crash
                # when run interactively on a login node.
                print_message(f"xshift {xshift}")
                for yshift in range(numshift):
                    for zshift in range(numshift):
                        # figure out where in the new dataset we are with this replication
                        idx = xshift * xfac + yshift * yfac + zshift
                        beg = idx * data.shape[0]
                        end = (idx + 1) * data.shape[0]
                        if dset == "Coordinates":
                            # shift coordinates
                            newds[beg:end, 0] = data[:, 0] + xshift * box[0]
                            newds[beg:end, 1] = data[:, 1] + yshift * box[1]
                            newds[beg:end, 2] = data[:, 2] + zshift * box[2]
                        elif dset == "ParticleIDs":
                            # generate new IDs
                            newds[beg:end] = np.arange(
                                id_ofs, id_ofs + newshape[0], dtype=np.int64
                            )
                            id_ofs += newshape[0]
                        else:
                            # simply write other datasets
                            newds[beg:end] = data[:]
                        # flush the output file (not really necessary)
                        ofile.flush()

print_message(f"Done. Remember: use scale factor {a} where appropriate!")
