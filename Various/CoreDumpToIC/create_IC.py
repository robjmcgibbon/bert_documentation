import numpy as np
import h5py
from new_read_particles import get_arrays

parts, _, gparts, sparts, bparts = get_arrays()

parts = parts[parts["id"] >= 0]
gparts = gparts[gparts["id"] >= 0]
sparts = sparts[sparts["id"] >= 0]
bparts = bparts[bparts["id"] >= 0]
bparts = bparts[:-5]

file = h5py.File("IC.hdf5", "w")

npart = parts.shape[0]
coords = np.zeros((npart, 3), dtype=np.float64)
coords[:, 0] = parts["x[0]"]
coords[:, 1] = parts["x[1]"]
coords[:, 2] = parts["x[2]"]
vs = np.zeros((npart, 3), dtype=np.float32)
vs[:, 0] = parts["v[0]"]
vs[:, 1] = parts["v[1]"]
vs[:, 2] = parts["v[2]"]
ms = np.zeros(npart, dtype=np.float32)
ms[:] = parts["mass"]
hs = np.zeros(npart, dtype=np.float32)
hs[:] = parts["h"]
us = np.zeros(npart, dtype=np.float32)
us[:] = parts["u"]
ids = np.zeros(npart, dtype=np.int64)
ids[:] = parts["id"]

group = file.create_group("PartType0")
group.create_dataset("Coordinates", data=coords)
group.create_dataset("Velocities", data=vs)
group.create_dataset("Masses", data=ms)
group.create_dataset("SmoothingLength", data=hs)
group.create_dataset("InternalEnergy", data=us)
group.create_dataset("ParticleIDs", data=ids)

ngpart = gparts.shape[0]
coords = np.zeros((ngpart, 3), dtype=np.float64)
coords[:, 0] = gparts["x[0]"]
coords[:, 1] = gparts["x[1]"]
coords[:, 2] = gparts["x[2]"]
vs = np.zeros((ngpart, 3), dtype=np.float32)
vs[:, 0] = gparts["v_full[0]"]
vs[:, 1] = gparts["v_full[1]"]
vs[:, 2] = gparts["v_full[2]"]
ms = np.zeros(ngpart, dtype=np.float32)
ms[:] = gparts["mass"]
ids = np.zeros(ngpart, dtype=np.int64)
ids[:] = gparts["id"]

group = file.create_group("PartType1")
group.create_dataset("Coordinates", data=coords)
group.create_dataset("Velocities", data=vs)
group.create_dataset("Masses", data=ms)
group.create_dataset("ParticleIDs", data=ids)

nspart = sparts.shape[0]
coords = np.zeros((nspart, 3), dtype=np.float64)
coords[:, 0] = sparts["x"][:, 0]
coords[:, 1] = sparts["x"][:, 1]
coords[:, 2] = sparts["x"][:, 2]
vs = np.zeros((nspart, 3), dtype=np.float32)
vs[:, 0] = sparts["v"][:, 0]
vs[:, 1] = sparts["v"][:, 1]
vs[:, 2] = sparts["v"][:, 2]
ms = np.zeros(nspart, dtype=np.float32)
ms[:] = sparts["mass"]
hs = np.zeros(nspart, dtype=np.float32)
hs[:] = sparts["h"]
ids = np.zeros(nspart, dtype=np.int64)
ids[:] = sparts["id"]
fts = np.zeros(nspart, dtype=np.float32)
fts[:] = sparts["birth_scale_factor"]

group = file.create_group("PartType4")
group.create_dataset("Coordinates", data=coords)
group.create_dataset("Velocities", data=vs)
group.create_dataset("Masses", data=ms)
group.create_dataset("SmoothingLength", data=hs)
group.create_dataset("ParticleIDs", data=ids)
group.create_dataset("StellarFormationTime", data=fts)

nbpart = bparts.shape[0]
coords = np.zeros((nbpart, 3), dtype=np.float64)
coords[:, 0] = bparts["x"][:, 0]
coords[:, 1] = bparts["x"][:, 1]
coords[:, 2] = bparts["x"][:, 2]
vs = np.zeros((nbpart, 3), dtype=np.float32)
vs[:, 0] = bparts["v"][:, 0]
vs[:, 1] = bparts["v"][:, 1]
vs[:, 2] = bparts["v"][:, 2]
ms = np.zeros(nbpart, dtype=np.float32)
ms[:] = bparts["mass"]
sms = np.zeros(nbpart, dtype=np.float32)
sms[:] = bparts["subgrid_mass"]
hs = np.zeros(nbpart, dtype=np.float32)
hs[:] = bparts["h"]
ids = np.zeros(nbpart, dtype=np.int64)
ids[:] = bparts["id"]

group = file.create_group("PartType5")
group.create_dataset("Coordinates", data=coords)
group.create_dataset("Velocities", data=vs)
group.create_dataset("Masses", data=ms)
group.create_dataset("SubgridMasses", data=sms)
group.create_dataset("SmoothingLength", data=hs)
group.create_dataset("ParticleIDs", data=ids)

boxSize = 12.5
grp = file.create_group("/Header")
grp.attrs["BoxSize"] = [boxSize, boxSize, boxSize]
grp.attrs["NumPart_Total"] = [npart, ngpart, 0, 0, nspart, nbpart]
grp.attrs["NumPart_Total_HighWord"] = [0, 0, 0, 0, 0, 0]
grp.attrs["NumPart_ThisFile"] = [npart, ngpart, 0, 0, nspart, nbpart]
grp.attrs["Time"] = 0.2140427
grp.attrs["NumFilesPerSnapshot"] = 1
grp.attrs["MassTable"] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
grp.attrs["Flag_Entropy_ICs"] = 0
grp.attrs["Dimension"] = 3

# Units
grp = file.create_group("/Units")
grp.attrs["Unit length in cgs (U_L)"] = 3.085678e24
grp.attrs["Unit mass in cgs (U_M)"] = 1.988410e43
grp.attrs["Unit time in cgs (U_t)"] = 3.085678e19
grp.attrs["Unit current in cgs (U_I)"] = 1.0
grp.attrs["Unit temperature in cgs (U_T)"] = 1.0

file.close()
