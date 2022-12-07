Scripts to generate a variety of maps for visualisation.

The scripts generate maps at different zoom levels and store them in `.npz`
files. These can potentially be transferred to another system. Plotting scripts
can directly load the `.npz` image cubes without having to reread the snapshot
file(s).

Files in this folder:
 - `make_zoom_maps.py`: Main map generating script. Contains a general function
   that can be used to generate maps for any snapshot at any zoom level.
 - `make_maps.py`: Basic example that uses the map generating function to make
   maps for the 3 different resolutions of the FLAMINGO 1 Gpc box.
 - `make_large_maps.py`: Same as the previous script, but then for the 2.8 Gpc
   FLAMINGO box.
