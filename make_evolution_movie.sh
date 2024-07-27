#!/bin/bash

box_size="1000"
#box_size="2800"
n_part="900"
#n_part="5040"
run="HYDRO_FIDUCIAL"
n_frame=200
box_frac=0.7

# Activate virtual environment
#TODO: Venv file is now in this dir
. /cosma/home/dp004/dc-mcgi1/python_env/movie/venv.sh

# Define variables
n_part=`printf '%04d' ${n_part}`
sim_name="L${box_size}N${n_part}/${run}"
dirname="/snap8/scratch/dp004/dc-mcgi1/movies/flamingo/${sim_name}/"
flamingo="/cosma8/data/dp004/flamingo/Runs/${sim_name}"

#TODO: Make sure using correct centre
# Create npz files
python -u Visualisations/ZoomMaps/make_maps_all_snapshots.py $box_size $n_part $run $box_frac

# Exracting limits from npz files
python -u Visualisations/PlotMaps/Evolution/find_limits.py $dirname "${dirname}/limits.yml" --nproc=10

# Adding redshifts to limits file
python -u Visualisations/PlotMaps/Evolution/add_redshift.py "${dirname}/limits.yml" "${flamingo}/output_list.txt" "${dirname}/limits_with_z.yml"

#TODO: Variable n_proc
# Creating frames
python -u Visualisations/PlotMaps/Evolution/plot_frames.py "${dirname}/limits_with_z.yml"  "${dirname}/frames" --nproc=10 --nframe="$n_frame"

# Copy files to laptop
# Set framerate such that runtime is ~20s
# $ffmpeg -framerate 10 -i dm_frame_%04d.png -c:v libx264 -pix_fmt yuv420p 0_dm.mp4
# $ffmpeg -framerate 10 -i star_frame_%04d.png -c:v libx264 -pix_fmt yuv420p 0_star.mp4


