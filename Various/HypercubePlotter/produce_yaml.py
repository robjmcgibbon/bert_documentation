#!/usr/bin/env python3

"""
produce_yaml.py

Creates the `.yml` files required to run hypercube-plotter for a given set
of hypercube simulations. It is assumed that the normal pipeline has already
been run on these simulations. The script can automatically run the morphology
pipeline, the conversion scripts in this directory, and rerun the CDDF script.

This script takes no command line arguments; all parameters are hardcoded
below.
"""

import subprocess
import glob
import os
import yaml

# run additional scripts?
do_morphology = False
do_cddf = False
do_sfr = False
do_gasev = False

# list all the simulations
folders = sorted(glob.glob("colibre_calibration_wave_5/*/"))

# get all the plots we want for hypercube-plotter; we will only read these from
# the pipeline output
with open("hypercube_plots.yml", "r") as handle:
    plot_params = yaml.safe_load(handle)
    plot_keys = plot_params.keys()

# loop over the simulations
for folder in folders:
    print(folder)
    run_nr = int(folder.split("/")[1])
    os.makedirs(f"{folder}/pipeline_output", exist_ok=True)
    if do_morphology:
        # run the morphology pipeline
        print("Running morphology pipeline...")
        cmd = (
            f"../build_env/bin/python3 morphology-pipeline"
            f" -C colibre_config"
            f" -i ../{folder}"
            f" -s colibre_0016.hdf5"
            f" -c halo_0016.properties"
            f" -n TEST"
            f" -g 10"
            f" -o pipeline_output"
            f" -M 1.e9"
            f" -j 16"
        )
        print(cmd)
        proc = subprocess.run(cmd, shell=True, cwd="morpholopy")
        if proc.returncode != 0:
            raise RuntimeError(f"Error while running {cmd}!")

    if do_cddf:
        # run the CDDF script
        print("Computing CDDF plots...")
        for snap in [9, 16]:
            cmd = (
                f"build_env/bin/python3 pipeline-configs/colibre/scripts/column_density_distribution_function.py"
                f" -C pipeline-configs/colibre"
                f" -c halo_0016.properties"
                f" -s colibre_{snap:04d}.hdf5"
                f" -d {folder}"
                f" -o {folder}/pipeline_output"
                f" -n TEST"
            )
            print(cmd)
            proc = subprocess.run(cmd, shell=True)
            if proc.returncode != 0:
                raise RuntimeError(f"Error while running {cmd}!")

    if do_sfr:
        # run the cosmic SFH script
        print("Computing SFH...")
        cmd = (
            f"build_env/bin/python3 convert_SFH.py"
            f" {folder}/SFR.txt"
            f" {folder}/colibre_0016.hdf5"
            f" {folder}/SFH.yml"
        )
        print(cmd)
        proc = subprocess.run(cmd, shell=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Error while running {cmd}!")

    if do_gasev:
        # run the cosmic HI/H2 abundance script
        print("Computing gas evolution...")
        cmd = (
            f"build_env/bin/python3 convert_gas_evolution.py"
            f" {folder}/statistics.txt"
            f" {folder}/colibre_0016.hdf5"
            f" {folder}/gas_evolution.yml"
        )
        print(cmd)
        proc = subprocess.run(cmd, shell=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Error while running {cmd}!")

    # combine plot data from all the various .yml files into a single one
    print("Generating combined YAML file...")
    yaml_data = {}
    # normal pipeline data
    with open(f"{folder}/data_0016.yml", "r") as handle:
        pipeline_data = yaml.safe_load(handle)
    for key in pipeline_data:
        if key in plot_keys:
            yaml_data[key] = pipeline_data[key]
    # CDDF plot data
    for snap in [9, 16]:
        with open(f"{folder}/colibre_{snap:04d}_cddf.yml", "r") as handle:
            cddf_data = yaml.safe_load(handle)
        for key in cddf_data:
            new_key = f"{key}_{snap:04d}"
            if new_key in plot_keys:
                yaml_data[new_key] = cddf_data[key]
    # SFH data
    with open(f"{folder}/SFH.yml", "r") as handle:
        SFH_data = yaml.safe_load(handle)
    for key in SFH_data:
        if key in plot_keys:
            yaml_data[key] = SFH_data[key]
    # gas evolution data
    with open(f"{folder}/gas_evolution.yml", "r") as handle:
        gasev_data = yaml.safe_load(handle)
    for key in gasev_data:
        if key in plot_keys:
            yaml_data[key] = gasev_data[key]
    # morphology pipeline data
    with open(f"{folder}/morphology_data_0016.yml", "r") as handle:
        morph_data = yaml.safe_load(handle)
    for key in morph_data["Median lines"]:
        if key in plot_keys:
            x = morph_data["Median lines"][key]["x centers"]
            y = morph_data["Median lines"][key]["y values"]
            x_unit = morph_data["Median lines"][key]["x units"]
            y_unit = morph_data["Median lines"][key]["y units"]
            yaml_data[key] = {
                "lines": {
                    "median": {
                        "centers": x,
                        "centers_units": x_unit,
                        "values": y,
                        "values_units": y_unit,
                    }
                }
            }

    # create a new .yml file that can serve as input to hypercube-plotter
    with open(f"hypercube_data/{run_nr}.yml", "w") as handle:
        yaml.safe_dump(yaml_data, handle)

    print("Done.")
