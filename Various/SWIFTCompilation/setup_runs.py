import sys

sys.path.append("/home/vandenbroucke/Documents/python_compile_script")

import clone
import compile
import simulation

# where to find swift
swift_url = "git@gitlab.cosma.dur.ac.uk:EAGLE/swift-colibre.git"
branch = "trim_subgrid"

# modules needed to compile and run
modules = [
    "intel_comp/2020-update2",
    "intel_mpi/2020-update2",
    "ucx/1.8.1",
    "parmetis/4.0.3-64bit",
    "parallel_hdf5/1.10.6",
    "fftw/3.3.8cosma7",
    "gsl/2.5",
]

# basic configuration (shared by all runs)
base_conf = [
    "--with-subgrid=COLIBRE",
    "--with-dust=T20",
    "--with-hydro=sphenix",
    "--with-kernel=quartic-spline",
    "--with-tbbmalloc",
    "--disable-hand-vec",
    "--enable-ipo",
    "--with-number-of-SNII-rays=8",
    "--with-parmetis",
]

# additional configuration for profiling runs
prof_conf = ["--enable-task-debugging", "--enable-mpiuse-reports"]

# first clone the repository (once)
swift_dir = "Code_trim_subgrid_clone"
clone.clone_swift(swift_dir, branch=branch, source_url=swift_url)
