#! /usr/bin/python3

import sys

sys.path.append("/home/vandenbroucke/Documents/python_compile_script")
import get_module_environment
import subprocess
import argparse
import os

argparser = argparse.ArgumentParser()
argparser.add_argument("--reconfigure", "-c", action="store_true")
argparser.add_argument("--threads", "-j", action="store", type=int, default=16)
argparser.add_argument("--tests", "-t", action="store_true")
args = argparser.parse_args()

env = get_module_environment.get_environment_for_modules(["SWIFT/1.0.0-Desktops"],
  module_path="/net/draco/data1/SWIFTSoftware/modules")
#env = get_module_environment.get_environment_for_modules([])

if args.reconfigure:
    df = subprocess.Popen("make distclean".format(args.threads), shell=True, env=env)
    df.wait()
    if df.returncode != 0:
        print("Error running 'make distclean'! Continuing...")
        if os.path.exists("Makefile"):
            os.remove("Makefile")

if not os.path.exists("Makefile"):
    cmd = [
        "./configure",
        "--silent",
#        "--with-cooling=const-lambda",
#        "--with-grackle=/home/vandenbroucke/.local",
#        "--with-subgrid=EAGLE-XL",
#        "--with-cooling=grackle_0",
#        "--enable-compiler-warnings",
#        "--with-black-holes=EAGLE",
#        "--with-chemistry=EAGLE",
#        "--with-feedback=GEAR",
#        "--with-stars=GEAR",
#        "--with-star-formation=GEAR",
        "--enable-option-checking",
        "--with-spmhd=direct-induction",
        "--with-adiabatic-index=2",
#        "--enable-naive-interactions",
#        "--enable-task-debugging",
#        "--enable-threadpool-debugging",
#        "--enable-cell-graph",
#        "--enable-debug",
#        "--enable-debugging-checks",
#        "--disable-optimization",
#        "--with-hydro=gizmo-mfv",
#        "--with-hydro-dimension=3",
#        "--with-kernel=quartic-spline",
#        "--with-metis=/home/vandenbroucke/Programs/metis-5.1.0-build",
#        "--disable-mpi",
#        "--with-riemann-solver=hllc",
#        "--with-ext-potential=constant",
#        "--enable-stars-density-checks=1",
#        "--enable-black-holes-density-checks=1",
#        "--with-stars-ghost-ntask=12",
#        "--with-stars-self-ntask=12",
#        "--with-hydro=phantom",
#        "--with-equation-of-state=isothermal-gas",
#        "--disable-hand-vec",
#        "--enable-ghost-statistics=10",
#        "--enable-dumper",
#        "CFLAGS='-DONLY_SUBTASKS'",
    ]

    cmd = " ".join(cmd)

    print("Running", cmd)
    df = subprocess.Popen(cmd, shell=True, env=env)
    df.wait()
    if df.returncode != 0:
        print("Configuration error!")
        exit(1)

df = subprocess.Popen("make -j {0}".format(args.threads), shell=True, env=env)
df.wait()
if df.returncode != 0:
    print("Compilation error!")
    exit(1)

if args.tests:
    df = subprocess.Popen("make check -j {0}".format(args.threads), shell=True, env=env)
    df.wait()
    if df.returncode != 0:
        print("Unit tests failed!")
        exit(1)
