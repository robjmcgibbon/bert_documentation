import unyt
from make_zoom_maps import create_maps

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
