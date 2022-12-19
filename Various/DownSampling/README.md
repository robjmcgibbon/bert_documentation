This folder contains two scripts that can be used to downsample SWIFT snapshots
by a given sampling fraction.

Downsampling means: randomly removing a large number of particles and particle
datasets, while rescaling some of the remaining datasets (e.g. masses) to
conserve physical properties. Since the new, downsampled snapshot is usually
much smaller than the original snapshot, we make sure the resulting snapshot
is converted into a single file. However, we make use of multi-snapshot files
in the initial sampling phase to speed up the downsampling.

The two scripts in this folder are:
 - `downsample_snapshot.py`: actual downsampling script. Takes the input
   snapshot (as a file prefix, without the `.<rank>.hdf5` or `.hdf5` extension)
   and the output snapshot name (prefix) as arguments, as well as the sampling
   fraction and a random seed that guarantees sampling reproducibility.
   Runs in parallel (by default using 32 processes).
 - `create_virtual_snapshot.py`: modified version of the script in the SWIFT
   repository (under `tools/`) with the same name that is used by the
   downsampling script to generate a virtual file for the downsampled snapshot
   pieces. The single file version of the snapshot is simply produced by
   copying all the datasets from this virtual dataset into a real file.
