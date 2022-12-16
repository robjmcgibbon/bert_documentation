import numpy as np
import glob
import re

maps = sorted(
    glob.glob("maps/*.dat"),
    key=lambda s: [
        int(t) if t.isdigit() else t.lower() for t in re.split("(\d+)", s)
    ],
)

res = 800
all_maps = np.zeros((len(maps), res, res // 2), dtype=np.uint8)
bounds = []
cumulative_map = np.zeros((res, res // 2), dtype=np.float64)
#global_min = np.finfo(np.float32).max
global_min = 0.
for i, mapname in enumerate(maps):
    this_map = np.fromfile(mapname, dtype=np.float32).reshape((res, res // 2)).astype(np.float64)
    cumulative_map += 10.0**this_map
    vmin = np.nanmin(this_map)
    vmax = np.nanmax(this_map)
    vmax += 1.0e-5
    bounds.append((vmin, vmax))
    #global_min = min(global_min, vmin)
    global_min = min(global_min, 10.**vmin)
    mask = np.isnan(this_map)
    this_map = 255 * (this_map - vmin) / (vmax - vmin)
    this_map = this_map.astype(np.uint8)
    this_map[mask] = 255
    all_maps[i] = this_map

#global_max = np.log10(np.nanmax(cumulative_map))
global_max = np.nanmax(cumulative_map)
cumul_min = np.nanmin(cumulative_map)
global_zimin = 0
global_zimax = len(maps)
zdiff = 0.05

map_minmax = ",".join([f"[{v[0]}, {v[1]}]" for v in bounds])
template = f"""
const global_CYmin = {global_min};
const global_CYmin_start = {cumul_min};
const global_CYmax = {global_max};
const global_zimin = {global_zimin};
const global_zimax = {global_zimax};
const zdiff = {zdiff:.2f};
const map_minmax = [{map_minmax}];
const resolution = {res};
"""

all_maps.tofile("lightcone_all_maps.dat")
with open("globals.js", "w") as ofile:
    ofile.write(template)
