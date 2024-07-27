import os
import sys

import h5py
import matplotlib.pyplot as plt
import numpy as np
import swiftsimio
import unyt

box_size = int(sys.argv[1])
n_part = int(sys.argv[2])
run = sys.argv[3]
n_frame = int(sys.argv[4])

sim_name = f'L{box_size:04d}N{n_part:04d}/{run}/'
flamingo_dir = f'/cosma8/data/dp004/flamingo/Runs/{sim_name}/'
output_dir = f'/snap8/scratch/dp004/dc-mcgi1/movies/flamingo/stars_sw/{sim_name}/'
os.makedirs(output_dir, exist_ok=True)

res = 8192
size = 700 * unyt.Mpc
zwidth = 20 * unyt.Mpc
if box_size == 1000:
    centre = unyt.unyt_array(
        [579.619106529648, 873.5596484955305, 832.4762741155331], units="Mpc"
    )  

# Load particles within this region
load_region = [ 
    [   
        (centre[0] - size/2),
        (centre[0] + size/2),
    ],  
    [   
        (centre[1] - size/2),
        (centre[1] + size/2),
    ],  
    [   
        (centre[2] - zwidth/2),
        (centre[2] + zwidth/2),
    ],  
]

# Region to plot after recentering particles
bcentre = unyt.unyt_array(
    [box_size/2, box_size/2, box_size/2], units="Mpc"
)  
region = [
        bcentre[0] - size/2,
        bcentre[0] + size/2,
        bcentre[1] - size/2,
        bcentre[1] + size/2,
        bcentre[2] - zwidth/2,
        bcentre[2] + zwidth/2,
]

zmin = 0
zmax = 15
a_range = np.linspace(1.0 / (1 + zmax), 1.0, n_frame)
z_range = 1.0 / a_range - 1.0

def get_flamingo_filename(snap):
    return f'{flamingo_dir}snapshots/flamingo_{snap:04d}/flamingo_{snap:04d}.hdf5'

def get_file_redshift(snap):
    filename = get_flamingo_filename(snap)
    with h5py.File(filename, 'r') as file:
        z = file['Header'].attrs['Redshift']
    return z

snap = 0
i_frame = 0
reload_data = True
while i_frame < n_frame:
    print(f'Frame: {i_frame}')

    # Check if curent redshift is still between the two loaded snapshots
    while z_range[i_frame] < get_file_redshift(snap+1):
        snap += 1
        reload_data = True

    if reload_data:
        try:
            data_1 = data_2
        except NameError:
            print(f'Loading snapshot {snap}')
            filename_1 = get_flamingo_filename(snap)
            mask_1 = swiftsimio.mask(filename_1, spatial_only=True)
            mask_1.constrain_spatial(load_region)
            data_1 = swiftsimio.load(filename_1, mask=mask_1)

        print(f'Loading snapshot {snap+1}')
        filename_2 = get_flamingo_filename(snap+1)
        mask_2 = swiftsimio.mask(filename_2, spatial_only=True)
        mask_2.constrain_spatial(load_region)
        data_2 = swiftsimio.load(filename_2, mask=mask_2)

        try:
            print(f'Sorting particles')
            ids_1 = data_1.stars.particle_ids.value
            argsort_1 = np.argsort(ids_1)
            ids_1 = ids_1[argsort_1]
            coords_1 = data_1.stars.coordinates.value[argsort_1]
            coords_1 = (coords_1 + bcentre.value - centre.value) % box_size

            ids_2 = data_2.stars.particle_ids.value
            argsort_2 = np.argsort(ids_2)
            ids_2 = ids_2[argsort_2]
            coords_2 = data_2.stars.coordinates.value[argsort_2]
            coords_2 = (coords_2 + bcentre.value - centre.value) % box_size

            # Find which ids in ids_1 are also in ids_2
            s_1 = np.searchsorted(ids_2, ids_1)
            m_1 = s_1 < ids_2.shape[0]
            m_1[m_1] = ids_2[s_1[m_1]] == ids_1[m_1]

            # Same the other way
            s_2 = np.searchsorted(ids_1, ids_2)
            m_2 = s_2 < ids_1.shape[0]
            m_2[m_2] = ids_1[s_2[m_2]] == ids_2[m_2]

            coords_1 = coords_1[m_1]
            coords_2 = coords_2[m_2]
        except AttributeError:
            print(f'No star particles found')
            coords_1 = np.zeros(shape=(0, 3))
            coords_2 = np.zeros(shape=(0, 3))
        reload_data = False

    # Interpolate positions
    a = 1 / (1 + z_range[i_frame])
    a_1 = 1 / (1 + get_file_redshift(snap))
    a_2 = 1 / (1 + get_file_redshift(snap+1))
    frac = (a - a_1) / (a_2 - a_1)
    positions = (1 - frac) * coords_1 + frac * coords_2 

    if not positions.shape[0]:
        i_frame += 1
        continue

    # Setting positions within swiftswimio object
    # Stars not present in both snapshots are moved to origin
    data_1.stars.coordinates *= 0
    data_1.stars.coordinates[argsort_1[m_1]] += positions * unyt.Mpc

    # TODO: Calculate smoothing lengths

    print('Creating projection')
    star_mass = swiftsimio.visualisation.projection.project_pixel_grid(
        data=data_1.stars,
        boxsize=data_1.metadata.boxsize,
        resolution=res,
        project="masses",
        parallel=True,
        region=region,
        backend="histogram",
    )
    # This unit stuff was lifted from one of Bert's scripts, I'm not sure it matters
    units = 1.0 / ((region[1] - region[0]) * (region[3] - region[2]))
    units.convert_to_units(1.0 / (region[0].units * region[2].units))
    units *= data_1.stars.masses.units
    star_mass = unyt.unyt_array(star_mass, units=units)
    star_mass.convert_to_units("g/cm**2")

    np.savez_compressed(f'{output_dir}/stars_{i_frame:04d}.npz', surfdens=star_mass)

    i_frame += 1

