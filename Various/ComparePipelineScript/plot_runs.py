import h5py
import glob
from birth_pressure_distribution import plot_birth_pressure_distribution
import multiprocessing as mp


def process_file(file):
    stylesheet = "mnras.mplstyle"
    with h5py.File(file, "r") as handle:
        name = handle["/Header"].attrs["RunName"].decode("utf-8")
        z = handle["/Header"].attrs["Redshift"][0]
        name = f"{name} (z = {z:.2f})"
    outputname = file.split("/")[1]
    plot_birth_pressure_distribution(name, outputname, stylesheet, file)
    return file


if __name__ == "__main__":

    mp.set_start_method("forkserver")

    folders = sorted(glob.glob("runs/*"))
    files = []
    for folder in folders:
        snaps = sorted(glob.glob(f"{folder}/*.hdf5"))
        if len(snaps) > 0:
            files.append(snaps[-1])

    pool = mp.Pool(32)
    count = 0
    ncount = len(files)
    for file in pool.imap_unordered(process_file, files):
        count += 1
        print(f"[{count:04d}/{ncount:04d}] {file} done.")
