#!/usr/bin/env python3

"""
check_completeness.py

Script to check the completeness of SOAP runs for the FLAMINGO simulations.

The script takes a FLAMINGO resolution folder (e.g. the default: "L1000N1800")
and the name of a specific simulation (e.g. "DMO_FIDUCIAL" or "HYDRO_FIDUCIAL").
It then checks for the existence of various sets of output files in a number
of locations:
 --member (-m): SOAP membership information files.
 --catalogue (-c): SOAP catalogue files.
 --downsampled (-d): Downsampled snapshots.
 --reduced (-r): Reduced snapshots.
 --all (-a): All of the above combined.

The existence is checked in a thorough way: every file is opened to ensure it
can actually be correctly opened. For SOAP catalogue files and reduced
snapshots, an additional check is performed to check the files have the correct
version:
 - Old SOAP catalogues were compressed in the wrong way and were missing the
   "Is Compressed" attribute for all datasets. We explicitly check that this
   attribute exists for an arbitrary dataset (SO/200_crit/SORadius).
 - Old reduced snapshots did not apply the reduction mask to the SOAP
   membership datasets (GroupNr_all, GroupNr_bound, Rank_bound), making these
   datasets larger than necessary (and practically useless). We now explicitly
   check that PartType1/Coordinates has the same number of particles as
   PartType1/GroupNr_all. This is by far the most expensive check we perform.

Since a lot of files are split over multiple files (e.g. membership information,
reduced snapshots), we first retrieve a full list of all expected files from
the actual snapshot files. We then use this list to determine the number of
snapshots (and hence SOAP catalogues and downsampled snapshots - 1 per snapshot)
and the number of files per snapshot (and hence membership files and reduced
snapshots - 1 per snapshot sub-file).
"""

from numpy import zeros, nonzero
import glob
import os
import multiprocessing as mp
import argparse
import h5py


def check_files(args):
    found = []
    for file in args[1][:-1]:
        ok = False
        if os.path.exists(file):
            try:
                with h5py.File(file, "r") as handle:
                    if args[1][-1] == "SOAP":
                        ok = "Is Compressed" in handle["SO/200_crit/SORadius"].attrs
                    elif args[1][-1] == "reduced":
                        if handle["Header"].attrs["NumPart_ThisFile"][1] == 0:
                            ok = True
                        else:
                            shape_coord = handle["PartType1/Coordinates"].shape[0]
                            shape_grp = handle["PartType1/GroupNr_all"].shape[0]
                            ok = shape_coord == shape_grp
                    else:
                        ok = True
            except:
                pass
        found.append(ok)
    return args[0], tuple(found)


if __name__ == "__main__":

    mp.set_start_method("forkserver")

    argparser = argparse.ArgumentParser()
    argparser.add_argument("run")
    argparser.add_argument("--member", "-m", action="store_true")
    argparser.add_argument("--catalogue", "-c", action="store_true")
    argparser.add_argument("--downsampled", "-d", action="store_true")
    argparser.add_argument("--reduced", "-r", action="store_true")
    argparser.add_argument("--folder", "-f", default="L1000N1800")
    argparser.add_argument("--all", "-a", action="store_true")
    args = argparser.parse_args()

    do_member = False
    do_catalogue = False
    do_downsampled = False
    do_reduced = False
    if args.member:
        do_member = True
    if args.catalogue:
        do_catalogue = True
    if args.downsampled:
        do_downsampled = True
    if args.reduced:
        do_reduced = True
    if args.all:
        do_member = True
        do_catalogue = True
        do_downsampled = True
        do_reduced = True

    snap_folder = f"/snap8/scratch/dp004/dc-vand2/FLAMINGO/{args.folder}/{args.run}"
    data_folder = (
        f"/cosma8/data/dp004/dc-vand2/FLAMINGO/ScienceRuns/{args.folder}/{args.run}"
    )
    flam_folder = f"/cosma8/data/dp004/flamingo/Runs/{args.folder}/{args.run}"
    #    data_folder = flam_folder

    snaps = sorted(glob.glob(f"{snap_folder}/snapshots/flamingo_????"))
    nrank = len(glob.glob(f"{snaps[0]}/flamingo_????.*.hdf5"))
    snaps = [snap[-4:] for snap in snaps]
    nsnap = len(snaps)
    nfile = nrank * nsnap

    pool = mp.Pool(32)

    if do_member:
        snap_member_full = [
            f"{snap_folder}/SOAP/membership_{snap}/membership_{snap}.{rank}.hdf5"
            for snap in snaps
            for rank in range(nrank)
        ]
        snap_member_comp = [
            f"{snap_folder}/SOAP_compressed/membership_{snap}/membership_{snap}.{rank}.hdf5"
            for snap in snaps
            for rank in range(nrank)
        ]
        data_member = [
            f"{data_folder}/SOAP/membership_{snap}/membership_{snap}.{rank}.hdf5"
            for snap in snaps
            for rank in range(nrank)
        ]
        flam_member = [
            f"{flam_folder}/SOAP/membership_{snap}/membership_{snap}.{rank}.hdf5"
            for snap in snaps
            for rank in range(nrank)
        ]
        member_checks = list(
            enumerate(
                zip(
                    flam_member,
                    data_member,
                    snap_member_comp,
                    snap_member_full,
                    [None] * len(data_member),
                )
            )
        )

        member_mask = zeros((nfile, 4), dtype=bool)
        for i, (fm, dm, smc, smf) in pool.imap_unordered(check_files, member_checks):
            member_mask[i, 0] = fm
            member_mask[i, 1] = dm
            member_mask[i, 2] = smc
            member_mask[i, 3] = smf
        print(f"Membership files: {member_mask.sum(axis=0)} out of {nfile}")
        snap_complete = member_mask.reshape((-1, nrank, 4)).min(axis=1)
        print(
            f"Number of complete membership snapshots: {snap_complete.sum(axis=0)} out of {nsnap}"
        )
        print("Missing:")
        for iloc, loc in enumerate(["flamingo", "final", "compressed", "SOAP"]):
            print(f" - {loc}:")
            snap_missing = nsnap - snap_complete[:, iloc].sum()
            if snap_missing > 0:
                if snap_missing == nsnap:
                    print("    All snapshots")
                else:
                    missing = [snaps[i] for i in nonzero(~snap_complete[:, iloc])[0]]
                    print(f"    snapshots {missing}")
            else:
                print("Nothing missing!")

    if do_catalogue:
        snap_SOAP_full = [
            f"{snap_folder}/SOAP/halo_properties_{snap}.hdf5" for snap in snaps
        ]
        snap_SOAP_comp = [
            f"{snap_folder}/SOAP_compressed/halo_properties_{snap}.hdf5"
            for snap in snaps
        ]
        data_SOAP = [
            f"{data_folder}/SOAP/halo_properties_{snap}.hdf5" for snap in snaps
        ]
        flam_SOAP = [
            f"{flam_folder}/SOAP/halo_properties_{snap}.hdf5" for snap in snaps
        ]
        SOAP_checks = list(
            enumerate(
                zip(
                    flam_SOAP,
                    data_SOAP,
                    snap_SOAP_comp,
                    snap_SOAP_full,
                    ["SOAP"] * len(data_SOAP),
                )
            )
        )

        SOAP_mask = zeros((nsnap, 4), dtype=bool)
        for i, (fm, dm, smc, smf) in pool.imap_unordered(check_files, SOAP_checks):
            SOAP_mask[i, 0] = fm
            SOAP_mask[i, 1] = dm
            SOAP_mask[i, 2] = smc
            SOAP_mask[i, 3] = smf
        print(f"Catalogue files: {SOAP_mask.sum(axis=0)} out of {nsnap}")
        print("Missing:")
        for iloc, loc in enumerate(["flamingo", "final", "compressed", "SOAP"]):
            print(f" - {loc}:")
            snap_missing = nsnap - SOAP_mask[:, iloc].sum()
            if snap_missing > 0:
                if snap_missing == nsnap:
                    print("    All snapshots")
                else:
                    missing = [snaps[i] for i in nonzero(~SOAP_mask[:, iloc])[0]]
                    print(f"    snapshots {missing}")
            else:
                print("Nothing missing!")

    if do_reduced:
        snap_red = [
            f"{snap_folder}/snapshots_reduced/flamingo_{snap}/flamingo_{snap}.{rank}.hdf5"
            for snap in snaps
            for rank in range(nrank)
        ]
        data_red = [
            f"{data_folder}/snapshots_reduced/flamingo_{snap}/flamingo_{snap}.{rank}.hdf5"
            for snap in snaps
            for rank in range(nrank)
        ]
        flam_red = [
            f"{flam_folder}/snapshots_reduced/flamingo_{snap}/flamingo_{snap}.{rank}.hdf5"
            for snap in snaps
            for rank in range(nrank)
        ]
        red_checks = list(
            enumerate(zip(flam_red, data_red, snap_red, ["reduced"] * len(data_red)))
        )

        red_mask = zeros((nfile, 3), dtype=bool)
        for i, (fm, dm, sm) in pool.imap_unordered(check_files, red_checks):
            red_mask[i, 0] = fm
            red_mask[i, 1] = dm
            red_mask[i, 2] = sm
        print(f"Reduced snapshots: {red_mask.sum(axis=0)} out of {nfile}")
        snap_complete = red_mask.reshape((-1, nrank, 3)).min(axis=1)
        print(
            f"Number of complete reduced snapshots: {snap_complete.sum(axis=0)} out of {nsnap}"
        )
        print("Missing:")
        for iloc, loc in enumerate(["flamingo", "data", "snap"]):
            print(f" - {loc}:")
            snap_missing = nsnap - snap_complete[:, iloc].sum()
            if snap_missing > 0:
                if snap_missing == nsnap:
                    print("    All snapshots")
                else:
                    missing = [snaps[i] for i in nonzero(~snap_complete[:, iloc])[0]]
                    print(f"    snapshots {missing}")
            else:
                print("Nothing missing!")

    if do_downsampled:
        snap_down = [
            f"{snap_folder}/snapshots_downsampled/flamingo_{snap}.hdf5"
            for snap in snaps
        ]
        data_down = [
            f"{data_folder}/snapshots_downsampled/flamingo_{snap}.hdf5"
            for snap in snaps
        ]
        flam_down = [
            f"{flam_folder}/snapshots_downsampled/flamingo_{snap}.hdf5"
            for snap in snaps
        ]
        down_checks = list(
            enumerate(zip(flam_down, data_down, snap_down, [None] * len(data_down)))
        )

        down_mask = zeros((nsnap, 3), dtype=bool)
        for i, (fm, dm, sm) in pool.imap_unordered(check_files, down_checks):
            down_mask[i, 0] = fm
            down_mask[i, 1] = dm
            down_mask[i, 2] = sm
        print(f"Downsampled snapshots: {down_mask.sum(axis=0)} out of {nsnap}")
        print("Missing:")
        for iloc, loc in enumerate(["flamingo", "data", "snap"]):
            print(f" - {loc}:")
            snap_missing = nsnap - down_mask[:, iloc].sum()
            if snap_missing > 0:
                if snap_missing == nsnap:
                    print("    All snapshots")
                else:
                    missing = [snaps[i] for i in nonzero(~down_mask[:, iloc])[0]]
                    print(f"    snapshots {missing}")
            else:
                print("Nothing missing!")
