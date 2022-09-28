import unyt
from make_zoom_maps import create_maps

centre = unyt.unyt_array(
    [579.619106529648, 873.5596484955305, 832.4762741155331], units="Mpc"
)

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
