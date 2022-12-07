import unyt
from make_zoom_maps import create_maps

"""
make_large_maps.py

Generate maps for the 2.8 Gpc FLAMINGO box at 4 different zoom levels,
centred on the most massive cluster.

This script assumes that the z=0 snapshot is soft-linked in the same folder
as L2800N5040.hdf5.

The position of the most massive cluster is hard-coded.
"""

# position of the most massive cluster in the box
centre = unyt.unyt_array(
    [908.108029106926, 654.1990705783709, 2222.372714962825], units="Mpc"
)

res = 8192
for filename in ["L2800N5040.hdf5"]:
    for boxsize in [2800.0, 700.0, 175.0, 45.0]:
        create_maps(
            filename,
            boxsize,
            res,
            centre=centre,
            zwidth=20.0 * unyt.Mpc,
            output_folder=f"L2800_zooms/{filename.removesuffix('.hdf5')}",
        )
