import unyt
from make_zoom_maps import create_maps

"""
make_maps.py

Generate maps for the 3 FLAMINGO resolutions at 3 different zoom levels,
centred on the most massive cluster in the 1 Gpc box.

This script assumes that the z=0 snapshots are soft-linked in the same folder
as
 - L1000N0900.hdf5
 - L1000N1800.hdf5
 - L1000N3600.hdf5

The position of the most massive cluster is hard-coded.
"""

# map centre: position of most massive cluster in the high-res FLAMINGO 1Gpc
# simulation
centre = unyt.unyt_array(
    [579.619106529648, 873.5596484955305, 832.4762741155331], units="Mpc"
)

# generate maps at 3 zoom levels, for the 3 different FLAMINGO resolutions
res = 8192
for filename in ["L1000N1800.hdf5", "L1000N0900.hdf5", "L1000N3600.hdf5"]:
    for boxsize in [1000.0, 250.0, 63.0]:
        create_maps(
            filename,
            boxsize,
            res,
            centre=centre,
            zwidth=20.0 * unyt.Mpc,
            output_folder=f"L1000_zooms/{filename.removesuffix('.hdf5')}",
        )
