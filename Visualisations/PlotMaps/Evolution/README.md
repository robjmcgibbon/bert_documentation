Set of scripts that can be used to generate an evolution movie of a FLAMINGO
simulation.

FLAMINGO runs have about 80 snapshots, which is largely insufficient to produce
a smooth movie. On top of that, the snapshots are not equally spaced in time,
nor redshift, nor scale factor.

To make a smooth movie with many frames and a natural time evolution, we first
create individual image maps and store them in `.npz` files. This uses the
usual script in Visualisations/ZoomMaps. We then run another script,
`find_limits.py` on these maps to generate a `.yml` file containing the minimum
and maximum value for each map. We need this information to determine an
appropriate colour scale that works for all maps. We then use yet another script,
`add_redshift.py` to extend this `.yml` file with redshift information for each
map. For this, we simply link the snapshot indices of the `.npz` files to
redshifts using the same `output_list.txt` file used by SWIFT to determine the
appropriate snapshot times.

With all of this information in hand, we can then make all the frames we want
by setting up a logarithmic time line in scale factor. For each scale factor
(or redshift) on this time line, we find the two images that have the closest
larger and smaller redshift, and then linearly interpolate the pixel values of
these images in log scale factor space. This results in a new image map, which
can then be plotted as a frame. This is achieved with the `plot_frames.py`
script. To avoid having to redo this operation very often, we save the image
frames without any additional annotations (so really just the raw pixels).

To turn this into an attractive movie, we finally combine the various frames
(and "zoom" frames generated for a different box size) into annotated movie
frames using `combine_frames.py`. This reads the raw `.png` images and replots
them in a more appealing way. This is much quicker than re-reading the `.npz`
images and redoing the interpolation. Some extra labels can be added to the
frames first (or even afterwards) using `add_labels.py`.

The movie itself is generated using `make_movie.sh`.

For testing, it can be useful to have some smaller `.npz` maps available. These
can be generated using `make_mini_frames.py`.
