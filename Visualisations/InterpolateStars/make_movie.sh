#!/bin/bash

box_size="1000"
n_part="1800"
run="HYDRO_FIDUCIAL"
n_frame=200
box_frac=0.7

# Activate virtual environment
. /cosma/home/dp004/dc-mcgi1/python_env/movie/venv.sh

# Define variables
n_part=`printf '%04d' ${n_part}`
sim_name="L${box_size}N${n_part}/${run}"

# Extract and interpolate stars
python -u interpolate_stars.py $box_size $n_part $run $n_frame
python -u plot_frames.py $box_size $n_part $run $n_frame

# Copy files to laptop
# Set framerate such that runtime is ~20s
# ffmpeg -framerate 10 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p 0_stars.mp4
