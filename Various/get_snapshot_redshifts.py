import h5py
import glob

# snaps = sorted(glob.glob("/cosma7/data/dp004/dc-chai1/nearly_final_model/I102_L25N188_I75_BH_BOOST_SLOPE_0p0/colibre_????.hdf5"))
snaps = sorted(glob.glob("Hypercube1/wdir_0/colibre_????.hdf5"))

with open("snapshot_redshifts.txt", "w") as ofile:
    for snap in snaps:
        with h5py.File(snap, "r") as ifile:
            z = ifile["/Header"].attrs["Redshift"][0]
        ofile.write(f"{snap.split('/')[-1]}\t{z:.2f}\n")
