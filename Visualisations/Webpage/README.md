Scripts used to generate the binary files that are required for the
interactive lightcone slider tool on the FLAMINGO web page.

This is a two step process:
 - `extract_maps.py` converts the full `.hdf5` lightcone maps into binary
files that only contain the map of interest, already projected into a full
sky Mollweide projection map, and already converted to single precision values.
We isolated this into a single script to allow parallel processing for different
HEALPix maps (since processing a single map can be quite slow).
 - `create_binary_map.py` reads the binary files and combines them into a single
highly compressed binary file (`lightcone_all_maps.dat`) and a `.js` file
containing some variables that the web page Javascript needs (`globals.js`).

Note that the manual compression done in `create_binary_map.py` is necessary
to avoid too much data transfer to the client browser. As it is, the compressed
map is still 21MB, which is quite a lot to load. The compression that is used
is tailored to this particular map (the dispersion measure) and only works if
the assumed scaling in this script is the same as in the Javascript that
uncompresses the map. It is therefore imporant to keep the Python and
Javascript scripts in tune.
