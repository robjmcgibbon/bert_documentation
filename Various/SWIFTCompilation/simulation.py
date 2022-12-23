#! /usr/bin/python3

import os
import shutil
import numpy as np


def setup_simulation_folder(
    folder_name,
    modules,
    swift_folder,
    swift_args,
    swift_params,
    name=None,
    numranks=1,
    numcores=28,
    queue="cosma7",
    time=3600.0,
    files=None,
    symlinks=None,
):

    if os.path.exists(folder_name):
        print('Error: folder "{0}" already exists!'.format(folder_name))
        exit(1)

    time_hh = int(np.floor(time / 3600.0))
    time_mm = int(np.floor((time - time_hh * 3600.0) / 60.0))
    time_ss = int(time - time_hh * 3600.0 - time_mm * 60.0)

    if time > 259200:
        print(
            "Error: more time requested than the 72 hrs limit: {0:02d}:{1:02d}:{2:02d}!".format(
                time_hh, time_mm, time_ss
            )
        )
        exit(1)

    if not os.path.exists(swift_folder):
        print("Error: swift folder does not exist!")
        exit(1)
    swift_exec = "{0}/examples/swift".format(os.path.realpath(swift_folder))
    if numranks > 1:
        swift_exec += "_mpi"

    if not os.path.exists(swift_exec):
        print('Error: could not find swift executable "{0}"!'.format(swift_exec))
        exit(1)

    os.makedirs(folder_name)

    if name is None:
        name = folder_name

    has_params = False
    if not files is None:
        for fname in files:
            if fname == swift_params:
                has_params = True
                break
    if not has_params:
        files.append(swift_params)
    for fname in files:
        if not os.path.exists(fname):
            print('Error: file "{0}" does not exist!'.format(fname))
            exit(1)
        shutil.copyfile(fname, "{0}/{1}".format(folder_name, os.path.basename(fname)))

    if not symlinks is None:
        for symlink in symlinks:
            if not os.path.exists(symlink):
                print('Error: file "{0}" does not exist!'.format(symlink))
                exit(1)
            os.symlink(
                os.path.realpath(symlink),
                "{0}/{1}".format(folder_name, os.path.basename(symlink)),
            )

    has_threads = False
    for arg in swift_args:
        if "--threads" in arg:
            has_threads = True
            break
    if not has_threads:
        swift_args.append("--threads={0}".format(numcores))

    with open("{0}/submit.slurm".format(folder_name), "w") as sfile:
        sfile.write("! /bin/bash\n")
        sfile.write("#SBATCH -J {0}\n".format(name))
        sfile.write("#SBATCH --ntasks {0}\n".format(numranks))
        sfile.write("#SBATCH --cpus-per-task={0}\n".format(numcores))
        sfile.write("#SBATCH -o {0}.%j.out\n".format(name))
        sfile.write("#SBATCH -e {0}.%j.err\n".format(name))
        sfile.write("#SBATCH -p {0}\n".format(queue))
        sfile.write("#SBATCH -A dp004\n")
        sfile.write(
            "#SBATCH -t {0:02d}:{1:02d}:{2:02d}\n".format(time_hh, time_mm, time_ss)
        )
        sfile.write("#SBATCH --exclusive\n\n")
        sfile.write("module purge\n\n")
        for module in modules:
            sfile.write("module load {0}\n".format(module))
        sfile.write("\n")
        if numranks > 1:
            sfile.write(
                "mpirun -np {0} {1} {2}\n".format(
                    numranks, swift_exec, " ".join(swift_args)
                )
            )
        else:
            sfile.write("{0} {1}\n".format(swift_exec, " ".join(swift_args)))


if __name__ == "__main__":

    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("folder", action="store")
    argparser.add_argument("--files", "-f", action="store", nargs="+", default=None)
    argparser.add_argument("--symlinks", "-s", action="store", nargs="+", default=None)
    args = argparser.parse_args()

    setup_simulation_folder(
        args.folder,
        ["OpenMPI"],
        "test_clone",
        ["--help", "--threads=1"],
        "test_job",
        1,
        28,
        "cosma7",
        3600.0,
        args.files,
        args.symlinks,
    )
