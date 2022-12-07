import numpy as np
import swiftsimio as sw
from swiftsimio.visualisation.smoothing_length_generation import (
    generate_smoothing_lengths,
)
import unyt
import time
import os

"""
make_zoom_maps.py

Create maps of the gas, DM, stellar and neutrino surface density and the
gas temperature and X-ray emission (ROSAT band).
The maps contain a projection of a slice with a specified thickness.
General script that can be used on any (FLAMINGO) snapshot, at any resolution
and for a specified zoom level centred on a specified position.

When run in standalone mode, the script plots the entire low resolution
FLAMINGO box.
"""


def create_maps(
    filename: str,
    boxsize: float,
    res: int,
    centre: unyt.unyt_array,
    zwidth: unyt.unyt_quantity = 20.0 * unyt.Mpc,
    output_folder: str = "final_zoom_maps",
):
    """
    Create maps for the given snapshot.

    Maps are output in a folder (output_folder) as .npz files, with a name
    set by the box size (boxsize) and resolution (res). 6 maps are created:
     - <output_folder>/L<boxsize>_<res>_gas_map_sigma.npz:
       Gas surface density (in g cm^-2).
     - <output_folder>/L<boxsize>_<res>_gas_map_temp.npz:
       Gas temperature (in K).
     - <output_folder>/L<boxsize>_<res>_gas_map_xray.npz:
       Gas X-ray luminosity in the ROSAT band (in erg/s).
     - <output_folder>/L<boxsize>_<res>_dm_map_sigma.npz:
       DM surface density (in g cm^-2).
     - <output_folder>/L<boxsize>_<res>_star_map_sigma.npz:
       Stellar surface density (in g cm^-2).
     - <output_folder>/L<boxsize>_<res>_neutrinoNS_map_sigma.npz:
       Noise-suppressed neutrino surface density (in g cm^-2). Note that this
       does not contain the constant background neutrino surface density.

    We use the "subsampled" backend for all maps, except for the stellar
    surface density map, where we simply use "histogram". The reason is that
    the stellar surface density map looks very artificial when smoothing is
    used (because it does not really make sense to require 50 neighbours for
    a lonely star particle in a small halo).

    Parameters:
     - filename: str
       Name of the snapshot file.
     - boxsize: float
       Size of the box that is mapped in the image. Sets the zoom level of the
       image.
     - res: int
       Resolution of the images. Number of pixels on the side.
     - centre: unyt.unyt_array or numpy.NDArray[float]
       Centre of the image. All coordinates are recentred on this position.
     - zwidth: unyt.unyt_quantity (default: 20.*unyt.Mpc)
       Width of the slice along the projection direction (the z axis).
     - output_folder: str
       Name of the folder where the output .npz files are stored.
    """

    # deal with cosmo_array input
    centre = unyt.unyt_array(centre)

    # generate output file names
    rname = f"L{boxsize:.0f}_{res}"
    sname = f"{output_folder}/{rname}_gas_map_sigma.npz"
    Tname = f"{output_folder}/{rname}_gas_map_temp.npz"
    Xname = f"{output_folder}/{rname}_gas_map_xray.npz"
    dname = f"{output_folder}/{rname}_dm_map_sigma.npz"
    stname = f"{output_folder}/{rname}_star_map_sigma.npz"
    nuname = f"{output_folder}/{rname}_neutrinoNS_map_sigma.npz"

    # make sure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # convert the box size into a unyt_quantity
    boxsize = boxsize * unyt.Mpc

    # set up the mask
    mask = sw.mask(filename)
    b = mask.metadata.boxsize

    xmin = centre[0] - 0.5 * boxsize
    xmax = centre[0] + 0.5 * boxsize
    ymin = centre[1] - 0.5 * boxsize
    ymax = centre[1] + 0.5 * boxsize
    zmin = centre[2] - 0.5 * zwidth
    zmax = centre[2] + 0.5 * zwidth

    load_region = [
        [xmin, xmax],
        [ymin, ymax],
        [zmin, zmax],
    ]
    print(load_region)
    bcentre = 0.5 * b
    region = [
        bcentre[0] - 0.5 * boxsize,
        bcentre[0] + 0.5 * boxsize,
        bcentre[1] - 0.5 * boxsize,
        bcentre[1] + 0.5 * boxsize,
        bcentre[2] - 0.5 * zwidth,
        bcentre[2] + 0.5 * zwidth,
    ]

    mask.constrain_spatial(load_region)

    # load the data
    data = sw.load(filename, mask=mask)

    do_gas = (
        (not os.path.exists(sname))
        or (not os.path.exists(Tname))
        or (not os.path.exists(Xname))
    )

    # recentre and wrap gas coordinates
    if do_gas:
        tic = time.time()
        data.gas.coordinates[:, :] += bcentre[None, :] - centre[None, :]
        data.gas.coordinates = np.mod(data.gas.coordinates, b[None, :])
        toc = time.time()
        print(f"Recentering gas coordinates took {toc-tic:.2f}s")

    # generate the surface density map (if it does not exist yet)
    if not os.path.exists(sname):
        tic = time.time()
        mass_map = sw.visualisation.projection.project_gas(
            data,
            resolution=res,
            project="masses",
            parallel=True,
            region=region,
            backend="subsampled",
        )
        mass_map.convert_to_units("g/cm**2")
        np.savez_compressed(sname, surfdens=mass_map)
        toc = time.time()
        print(f"Generating gas surface density map took {toc-tic:.2f}s")
    elif (not os.path.exists(Tname)) or (not os.path.exists(Xname)):
        # load the map, since we need it for the temperature or X-ray
        # normalisation
        mass_map = unyt.unyt_array(np.load(sname)["surfdens"], units="g/cm**2")
        print("Loaded existing gas surface density map")
    else:
        print("Gas surface density map exists, not loading it")

    # generate the temperature map (if it does not exist yet)
    if not os.path.exists(Tname):
        tic = time.time()
        data.gas.mass_weighted_var = data.gas.masses * data.gas.temperatures
        mass_weighted_temp_map = sw.visualisation.projection.project_gas(
            data,
            resolution=res,
            project="mass_weighted_var",
            parallel=True,
            region=region,
            backend="subsampled",
        )
        mass_weighted_temp_map.convert_to_units("K*g/cm**2")
        temp_map = mass_weighted_temp_map / mass_map
        temp_map.convert_to_units("K")
        np.savez_compressed(Tname, temp=temp_map)
        toc = time.time()
        print(f"Generating gas temperature map took {toc-tic:.2f}s")
    else:
        print("Gas temperature map already exists")

    # generate the X-ray map (if it does not exist yet)
    if not os.path.exists(Xname):
        tic = time.time()
        data.gas.mass_weighted_var = data.gas.masses * data.gas.xray_luminosities.ROSAT
        mass_weighted_xray_map = sw.visualisation.projection.project_gas(
            data,
            resolution=res,
            project="mass_weighted_var",
            parallel=True,
            region=region,
            backend="subsampled",
        )
        mass_weighted_xray_map.convert_to_units("erg/s*g/cm**2")
        xray_map = mass_weighted_xray_map / mass_map
        xray_map.convert_to_units("erg/s")
        np.savez_compressed(Xname, rosat=xray_map)
        toc = time.time()
        print(f"Generating gas Xray map took {toc-tic:.2f}s")
    else:
        print("Gas Xray map already exists")

    # force unload of gas data?
    # not sure if this works, but since the memory footprint of the script is
    # quite large, it is worth a try
    data.gas.coordinates = None
    data.gas.masses = None
    data.gas.temperatures = None
    data.gas.xray_luminosities.ROSAT = None
    data.gas.mass_weighted_var = None

    # generate the DM surface density map (if it does not exist yet)
    if not os.path.exists(dname):
        # recentre and wrap dm coordinates
        tic = time.time()
        data.dark_matter.coordinates += bcentre[None, :] - centre[None, :]
        data.dark_matter.coordinates = np.mod(data.dark_matter.coordinates, b[None, :])
        toc = time.time()
        print(f"Recentering DM coordinates took {toc-tic:.2f}s")

        # generate smoothing lengths
        tic = time.time()
        data.dark_matter.smoothing_length = generate_smoothing_lengths(
            data.dark_matter.coordinates,
            data.metadata.boxsize,
            kernel_gamma=1.8,
            neighbours=57,
            speedup_fac=2,
            dimension=3,
        )
        toc = time.time()
        print(f"Generating dark matter smoothing lengths took {toc-tic:.2f}s")

        tic = time.time()
        dm_mass = sw.visualisation.projection.project_pixel_grid(
            data=data.dark_matter,
            boxsize=data.metadata.boxsize,
            resolution=res,
            project="masses",
            parallel=True,
            region=region,
            backend="subsampled",
        )
        units = 1.0 / ((region[1] - region[0]) * (region[3] - region[2]))
        units.convert_to_units(1.0 / (region[0].units * region[2].units))
        units *= data.dark_matter.masses.units
        dm_mass = unyt.unyt_array(dm_mass, units=units)
        dm_mass.convert_to_units("g/cm**2")
        np.savez_compressed(dname, surfdens=dm_mass)
        toc = time.time()
        print(f"Generating DM map took {toc-tic:.2f}s")
    else:
        print("DM map already exists")

    # try to reduce the memory footprint by unloading data (not sure if this
    # has an impact)
    data.dark_matter.smoothing_length = None
    data.dark_matter.coordinates = None
    data.dark_matter.masses = None

    # generate the stellar surface density map (if it does not exist yet)
    if not os.path.exists(stname):
        # recentre and wrap star coordinates
        tic = time.time()
        data.stars.coordinates += bcentre[None, :] - centre[None, :]
        data.stars.coordinates = np.mod(data.stars.coordinates, b[None, :])
        toc = time.time()
        print(f"Recentering star coordinates took {toc-tic:.2f}s")

        tic = time.time()
        star_mass = sw.visualisation.projection.project_pixel_grid(
            data=data.stars,
            boxsize=data.metadata.boxsize,
            resolution=res,
            project="masses",
            parallel=True,
            region=region,
            backend="histogram",
        )
        units = 1.0 / ((region[1] - region[0]) * (region[3] - region[2]))
        units.convert_to_units(1.0 / (region[0].units * region[2].units))
        units *= data.stars.masses.units
        star_mass = unyt.unyt_array(star_mass, units=units)
        star_mass.convert_to_units("g/cm**2")
        np.savez_compressed(stname, surfdens=star_mass)
        toc = time.time()
        print(f"Generating stellar surface density map took {toc-tic:.2f}s")
    else:
        print("Stellar surface density map already exists")

    # try to reduce the memory footprint by unloading data (not sure if this
    # has an impact)
    data.stars.smoothing_length = None
    data.stars.coordinates = None
    data.stars.masses = None

    # generate the neutrino surface density map (if it does not exist yet)
    if not os.path.exists(nuname):
        data.neutrinos.weighted_masses = data.neutrinos.masses * data.neutrinos.weights
        tic = time.time()
        data.neutrinos.coordinates += bcentre[None, :] - centre[None, :]
        data.neutrinos.coordinates = np.mod(data.neutrinos.coordinates, b[None, :])
        toc = time.time()
        print(f"Recentering neutrino coordinates took {toc-tic:.2f}s")

        tic = time.time()
        data.neutrinos.smoothing_length = generate_smoothing_lengths(
            data.neutrinos.coordinates,
            data.metadata.boxsize,
            kernel_gamma=1.8,
            neighbours=57,
            speedup_fac=2,
            dimension=3,
        )
        toc = time.time()
        print(f"Generating neutrino smoothing lengths took {toc-tic:.2f}s")

        tic = time.time()
        nu_mass = sw.visualisation.projection.project_pixel_grid(
            data=data.neutrinos,
            boxsize=data.metadata.boxsize,
            resolution=res,
            project="weighted_masses",
            parallel=True,
            region=region,
            backend="subsampled",
        )
        units = 1.0 / ((region[1] - region[0]) * (region[3] - region[2]))
        units.convert_to_units(1.0 / (region[0].units * region[2].units))
        units *= data.neutrinos.weighted_masses.units
        nu_mass = unyt.unyt_array(nu_mass, units=units)
        nu_mass.convert_to_units("g/cm**2")
        np.savez_compressed(nuname, surfdens=nu_mass)
        toc = time.time()
        print(f"Generating neutrino map took {toc-tic:.2f}s")
    else:
        print("Neutrino map already exists")

    # try to reduce the memory footprint by unloading data (not sure if this
    # has an impact)
    data.neutrinos.smoothing_length = None
    data.neutrinos.coordinates = None
    data.neutrinos.masses = None
    data.neutrinos.weights = None
    data.neutrinos.weighted_masses = None

    # force memory release (not sure if this works)
    del data
    del mask


if __name__ == "__main__":
    """
    Standalone mode.
    """

    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("output_folder")
    args = argparser.parse_args()

    filename = "L1000N0900.hdf5"

    res = 1024
    boxsize = 100.0

    centre = [500.0 * unyt.Mpc, 500.0 * unyt.Mpc, 500.0 * unyt.Mpc]

    create_maps(filename, boxsize, res, centre, 20.0 * unyt.Mpc, args.output_folder)
