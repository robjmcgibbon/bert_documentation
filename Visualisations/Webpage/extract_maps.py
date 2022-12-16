import numpy as np
import h5py
import healpy
import unyt

def extract_map(data, name):

    res = 800
    mollproj = healpy.projector.MollweideProj(xsize=res)

    pdata = mollproj.projmap(
        data, lambda x, y, z: healpy.vec2pix(1024, x, y, z)
    )

    mask = pdata < 0.0
    pdata[mask] = np.nan

    logpdata = np.log10(pdata).astype(np.float32)
    logpdata.tofile(name)


for i in range(68):
    shell = f"lightcone0_shells/shell_{i}/lightcone0.shell_{i}.0.hdf5"
    with h5py.File(shell, "r") as file:
        conversion = file["DM"].attrs["Conversion factor to CGS (not including cosmological corrections)"][0]
        data = unyt.unyt_array(file["DM"][:]*conversion, units="cm**(-2)")
    data.convert_to_units("pc/cm**3")

    extract_map(data.value, f"maps/shell_{i}.dat")
