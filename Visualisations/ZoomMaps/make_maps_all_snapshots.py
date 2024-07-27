import sys

import numpy as np
import unyt

from make_zoom_maps import create_maps

"""
make_maps.py

Generate maps for the all snapshots for a FLAMINGO simulation,
centred on the most massive cluster in the 1 Gpc box.

The position of the most massive cluster is hard-coded.
"""

box_size = int(sys.argv[1])
n_part = int(sys.argv[2])
run = sys.argv[3]
box_frac = float(sys.argv[4])

# map centre: position of most massive cluster
if box_size == 1000:
    centre = unyt.unyt_array(
        [579.619106529648, 873.5596484955305, 832.4762741155331], units="Mpc"
    )
elif box_size == 2800:
    centre = unyt.unyt_array(
        [908.108029106926, 654.1990705783709, 2222.372714962825], units="Mpc"
    )

res = 8192
zwidth = 20.0 * unyt.Mpc
sim_name = f'L{box_size:04d}N{n_part:04d}/{run}/'
output_dir = f'/snap8/scratch/dp004/dc-mcgi1/movies/flamingo/{sim_name}'

flamingo_dir = f'/cosma8/data/dp004/flamingo/Runs/{sim_name}'
redshifts = np.loadtxt(flamingo_dir+'output_list.txt')
for snap in range(len(redshifts)):
    print(f'Creating maps for snapshot {snap}')
    filename = f'{flamingo_dir}/snapshots/flamingo_{snap:04d}/flamingo_{snap:04d}.hdf5'
    arg_list = []
    # TODO: Multiprocessing
    create_maps(
        filename,
        box_size*box_frac,
        res,
        centre=centre,
        zwidth=zwidth,
        output_folder=f'{output_dir}/snapshot_{snap:04d}',
    )
