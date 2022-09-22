# Scaling tests

Scripts and files that are useful for setting up and automating scaling
tests.

## Purpose of a scaling test

Cosmological simulations are not only non-linear in their physics, but
also in the way they progress. While the early, high redshift regime is
dominated by long-range gravity (handled by the FFTW mesh), later stages
are dominated by hydrodynamics in small, high density regions. Star
formation and stellar feedback peaks around redshift 2 and then slowly
decreases again.

Since all of these aspects are implemented in SWIFT in very distinct
ways, it is close to impossible to predict the runtime, memory load and
efficiency of a SWIFT simulation using only information at early times.
Predicting these from smaller simulations is also not straigthforward,
since large simulations (especially using large numbers of MPI ranks)
tend to behave quite differently from their smaller counterparts.

In order to run a SWIFT simulation that is somewhat representative of a
late-time simulation without having to simulate the early times for
real, we developed a replication technique based on a smaller
simulation. The idea is to use a late-time snapshot from an existing run
with a similar SWIFT version (_similar_ because we want a representative
dynamic range in particle properties, _not the same_, meaning this is a
much more powerful technique than e.g. using restart files). This
snapshot is converted into an initial condition file and replicated
along its coordinates axes to generate a particle load representative
for a larger simulation. Since the replication can only work with the
structures contained in the original snapshot, this will not give you
the same range of structures you would find in a simulation that was
actually this large (some massive clusters will be missing). The time
step hierarchy will initially also be a lot more uniform than can be
expected in a real simulation, although we noticed that it diverges
quite quickly. Despite these drawbacks, this still allows you to
simulate a representative memory load and identify bottlenecks caused by
running SWIFT at that stage in the evolution on that scale.

## Generating initial conditions

The script `convert_snap_to_ic.py` contained within this folder converts
a SWIFT snapshot into an IC file. It was originally written for the
COLIBRE project, and was since successfully applied to both COLIBRE,
EAGLE-XL and FLAMINGO snapshots. The script only copies over (and if
necessary renames) datasets that are required for the IC, so unless a
new required dataset is added at some point, it should also be directly
applicable to other models.

There are some things you need to be aware of when using this script.

First of all, this script is not parallelised. The main reason is that
using parallel HDF5 in Python (with `h5py` and `mpi4py`) is a bit
cumbersome, while other ways to parallelise the script would not work
because only one process is allowed to write to an HDF5 file. Because
the script is not parallel, it should preferably be used on a login
node. The memory footprint (about as large as the largest single dataset
in the original snapshot after decompression), and the actual active CPU
usage are quite limited, since most of the time is spent in I/O. Running
on the login node should therefore not be too problematic. However, the
wall clock time can be quite large, especially for a large replication
factor.

Second, the resulting IC file can become quite large. This can cause
problems on Lustre file systems if the file striping is not set
appropriately. To handle very large files, it is recommended to apply
maximal Lustre striping:
```
> lfs setstripe -c -1 FILENAME
```
where `FILENAME` is the name of the IC file you want to create. This
command needs to be run before the file is actually created.

## Adapting parameter files

To start a SWIFT simulation using the newly created IC, you need to make
sure the scale factor parameters in various parameter files are set to
appropriate values. SWIFT will crash if these numbers are not compatible
with the scale factor in the IC file, which is the same as in the
snapshot file used to generate the IC. To facilitate this, the script
outputs the scale factor as encountered in the snapshot file. The
following is a non-exhaustive list of parameters that need to be changed
accordingly:
```
Cosmology:a_begin
FOF:scale_factor_first
Snapshots:scale_factor_first
Statistics:scale_factor_first
```

If you use any kind of output list for the simulation, you also need to
make sure all scale factor entries smaller than the current IC scale
factor are removed, since they will also lead to SWIFT crashes.

Since the IC will contain all types of particles and uses the snapshot
convention for properties where this matters, the following parameters
values need to be used in the `InitialConditions` parameter block:
```
InitialConditions:
  cleanup_h_factors: 0
  cleanup_smoothing_lengths: 0
  cleanup_velocity_factors: 0
  generate_gas_in_ics: 0
  periodic: 1
  remap_ids: 0
```
The IC file name obviously needs to be set to the name of the newly
generated file.

If you replicated the snapshot to generate a large box, you will also
need to adapt some parameters that change with the particle number.
Again, here is a non-exhaustive list:
```
Gravity:mesh_side_length
Gravity:distributed_mesh
Scheduler:max_top_level_cells
Snapshots:distributed
```
The `distributed_mesh` and `distributed` parameters are recommended for
really large runs, to reduce the gravity mesh size per rank and the I/O
overhead. The former requires the use of the `--enable-mpi-mesh-gravity`
configuration option for SWIFT (and a working parallel FFTW library).

## Running SWIFT

Once the IC file has been created and the parameter file(s) adjusted
according to the new IC file and starting scale factor, you can run
SWIFT as if this was just a normal simulation. However, since the whole
point of a scaling test is to gather performance statistics, you should
not just run the simulation until redshift 0, but only run it for a
limited amount of time. To this end, you can use the `-n NUMBER` runtime
argument for SWIFT, with `NUMBER` the number of steps you want to run
for (recommended values range from 100-2000).

To get the best performance information, it is also recommended to
enable task and threadpool debugging when configuring SWIFT:
```
> ./configure \
    --enable-task-debugging \
    --enable-threadpool-debugging \
    ...OTHER OPTIONS...
```
When running the simulation, you should then manually activate
additional task and threadpool plot output, using respectively the
`-y STEP` and `-Y STEP` runtime arguments for SWIFT, where `STEP` is
the interval (in SWIFT steps) between successive outputs. Note that this
will generate a lot of (possibly large) text files!

Other useful configuration options (that generate even more output files)
are
```
--enable-memuse-reports
--enable-mpiuse-reports
```
These are however less important, since they are only useful to analyse
very specific performance problems.

Finally, you also want to make sure to run with maximum verbosity:
```
> ./swift --verbose 2 ...OTHER ARGUMENTS...
```

## Automatically setting up a run directory

When running scaling tests, it is useful to run these at a few different
redshifts (e.g. z=5, z=2, z=0.1) to cover a couple of different stages
in the evolution. It might also be useful to run the scaling tests with
multiple different versions of SWIFT or different sets of parameters. To
facilitate this, it is strongly recommended to set up some scripts to
automate this process.

Before diving into this and introducing the example scripts contained in
this folder, it is important to introduce the concept of a _sandbox_,
which helps a lot to impose structure when dealing with large numbers of
runs.

The sandbox concept essentially means that an individual run should be,
as much as possible, self-contained. Each simulation consists of _input_
that is fed to an _executable_, which then results in specific _output_.
The _output_ for any unique combination of _input_ and _executable_ is
unique, but the _input_ and _executable_ can both be shared with other
simulations. It is quite natural to put the _output_ in a separate
directory, but for the _input_ and _executable_ this is usually less
common practice. The _sandbox_ is therefore a generalisation of the
directory to multiple files that are not necessarily in the same
directory: it is an environment that contains _input_, _executable_ and
_output_ simultaneously, and isolates them from other possible _input_
and _executable_ versions. The sandbox guarantees the persistence of the
combination _input_-_executable_-_output_ after a run has finished.

Within a file system, it is possible to create such a sandbox
environment within a single directory, without necessarily having to
copy over all the files. This can very easily be achieved by using soft
links. A soft link to a file is created using the `ln` command:
```
> ln -s PATH_TO_ORIGINAL_FILE SOFT_LINK_NAME
```
This command will create a new file or folder like object in the current
working directory with the name `SOFT_LINK_NAME`. When any file or
folder operation is performed on this object, the OS will automatically
redirect that operation to `PATH_TO_ORIGINAL_FILE`, as if the operation
was accessing that path in the first place. To find out the actual path
pointed to by a soft link, you can use `readlink`:
```
> readlink -f SOFT_LINK_NAME
```
The `-f` is quite useful, since it makes `readlink` work for any path,
also paths that are not soft links. The command will then simply return
the absolute path to the file/folder that is passed on as the argument.

When setting up the simulation sandbox, we can hence create a directory
and then copy or soft link all the input files and executables into that
directory. We then set up the run script(s) and parameter file(s) as if
all the files were actually present in that folder. If we later want to
move the sandbox to a different location, we can simply copy the entire
folder, and everything should still work. Particularly helpful is that
the copy command `rsync` has additional flags that tell it how to
treat soft links:
```
rsync -l ORIGIN DESTINATION
```
will copy soft links in `ORIGIN` to `DESTINATION` as soft links that still
link to the same file.
```
rsync -L ORIGIN DESTINATION
```
will resolve the soft links in `ORIGIN` and will copy the actual files
they point to into `DESTINATION`. This is particularly useful when
moving to a new machine where the original file locations are no longer
accessible, e.g. from `snap7` to `snap8` on COSMA.

We are left with the important question of what files to soft link and
what files to copy. There are no clear rules, but some recommendations:
 1. Files that are large (>100 MB or so) should preferably be soft
linked, since copying them would use a lot more disk space. For SWIFT
simulations, these are typically data files like cooling tables, which
do not change very often. These files are usually also versioned, which
means that their name changes if their contents changes. It is very
unlikely that a soft link pointing to such a file will suddenly resolve
into a different file.
 2. Files that are small and/or subject to regular change should be
copied. A prime example are parameter files, which can change between
code versions and are therefore naturally hard to share between
different simulations. Run and batch scripts are also good candidates
for copying, since you might want to make changes to these after the
sandbox has been created to deal with unexpected issues.
 3. Executables should in principle be soft linked, since that makes it
a lot easier to link them to a specific source code version. This is
however a bit dangerous, since executable files will change if the code
is recompiled. You should therefore only soft link executables that are
versioned in some way already, e.g. by creating a different copy of the
source code folder for each version or by configuring and compiling
out-of-source builds (where the same source code is shared by multiple
different builds with different configuration options). A good reason
not to copy executables is that executables are naturally bound to a
specific machine, so copying them over to another machine will (most
likely) not work.

With all of this explained, it is time to introduce some scripts that can
help to create sandboxed simulation directories:
 - `setup_simulation_directory.py` creates a directory with a given name
and copies/soft links files in two text files that can be passed on as
optional arguments `--copy` and `--link`. Two example files are
provided, `colibre_copy_files.txt` and `colibre_link_files.txt`, with
example lists of files you might want to include (taken from a COLIBRE
run).

## Analysing run performance

The following questions can or should be answered based on a (running)
scaling test simulation:
 1. How much memory is the run using?
 2. How efficiently is the run using its resources?
 3. Is the run behaving as expected?
 4. How large is the output of the run?
 5. Can the run performance be improved by fine-tuning parameters?
 6. How does the run performance compare with other (smaller) runs?

### Memory usage

The first point is very important, since it is the main factor that
determines what simulation can be run on a machine; if a run does not
fit in memory, it cannot be done. Unfortunately, this is also by far the
hardest aspect to analyse. If possible, it is best to try to monitor the
memory usage during the run, since that allows for some more powerful
monitoring.

The easiest way to get a feeling for the memory usage of a run is by
running `top`. This command (that wraps around the very powerful by
practically hard to use `ps` command) displays information about all
running processes on a machine, including CPU and memory usage. _This
machine_ unfortunately means it only works if you are logged in to the
same machine as where SWIFT is running, which is usually a computing
node and not a login node (or better, _should_ be a computing node and
not a login node).

There are some workarounds. The first workaround is that SLURM actually
allows you to attach a new process to an already running job, if you know
that job's `JOBID`:
```
srun --overlap --pty --jobid JOBID /bin/bash
```
For convenience, this folder contains the `attach_to_job.sh` script,
which does exactly this. Once you have a running `bash` terminal, you
can simply execute `top` there. The drawbacks of this method are
 1. You can only attach `bash` to the first node in the allocation, so
you only get information about one node.
 2. This is quite an obscure SLURM feature, meaning that not all systems
enable it (COSMA allows it, but COSMA support was not aware of its
existence until recently).

An alternative is to directly `ssh` into a computing node, which is
almost always not allowed. COSMA support can in principle give you that
permission, but it is quite unlikely they will do so unless they really
trust you. This is the only way to directly access any node in an
allocation.

On COSMA, all nodes come equiped with Performance Co-Pilot (PCP)
(<https://www.dur.ac.uk/icc/cosma/support/usage/pcp/>), which provides
an alternative way to monitor resource usage. The script `smart-pmstat`
in this folder provides a convenient wrapper that automatically calls
`pmstat` for all the nodes that are running a job with a known `JOBID`.
PCP has many more powerful tools, but the author has never used any of
these in practice.

Once the job is finished, most information about its runtime memory
usage is lost. There is however a way to at least recover the peak
memory usage, using `sacct`:
```
sacct -j $SLURM_JOBID --format=JobID,JobName,Partition,AveRSS,MaxRSS,AveVMSize,MaxVMSize,Elapsed,ExitCode
```
This line can be directly added to the end of a job script, in which
case SLURM will automatically replace the `$SLURM_JOBID` with the
appropriate `JOBID`. The output of `sacct` is quite concise and usually
(but not always) limited to a single node in the allocation.

## Run efficiency

When considering run efficiency, we are mostly interested in load
balancing between different MPI ranks, and between different threads on
one rank. This is where the task and threadpool plots come in very handy
(see
<https://swift.dur.ac.uk/docs/AnalysisTools/index.html#task-and-threadpool-plots-and-analysis-tools>).
Note that the task plot files can become very large for large numbers of
threads and ranks, so that it is recommended to run the corresponding
analysis script (`process_plot_tasks_MPI.py`) on a machine with
sufficient memory and using a lot of parallel processes (the `--nproc`
argument for the script). Time steps with similar sizes (in terms of
number of active particles) usually have similar task profiles, so it is
best to focus the analysis on a small number of steps with very
different sizes, as can easily be deduced from the size of the task plot
file.

Task bars in a task plot can sometimes be so small that they are
invisible. This could lead to the wrong conclusion that all threads are
doing nothing, while in truth they are active but just very badly
balanced. To help visualise this, the script `task_plot_heatmap.py` in
this folder can be used to convert the task plot file into a 2D
histogram of task activity. This histogram can be converted into a
heatmap showing the thread activity over time, which in turn can also be
used to plot the thread efficiency as a function of time and the average
active time fraction per thread.

Another way to look at the run efficiency is by analysing the dead time
per step, which is part of the `timesteps_xxx.txt` log file written by
SWIFT. The analysis pipeline contains some scripts to plot useful
statistics for these files:
 - [Dead time evolution](https://github.com/SWIFTSIM/pipeline-configs/blob/master/colibre/scripts/deadtime_evolution.py)
Plot the evolution of the dead time during a run. Also computes the
average dead time.
 - [Dead time versus step size](https://github.com/SWIFTSIM/pipeline-configs/blob/master/colibre/scripts/deadtime_timebin_hist.py)
Plot a histogram of the average dead time for a given step size. In a
"normal" run, the steps of intermediate size have the highest relative
amount of dead time.
