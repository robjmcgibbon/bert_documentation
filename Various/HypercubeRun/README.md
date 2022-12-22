The scripts in this directory can be used to set up and run a (COLIBRE)
hypercube. They were specifically created to run a hypercube in which the
birth pressure dependent feedback parameters were varied, but most of the
machinery is more generally applicable.

The process consists of a number of steps:
 1. `create_hypercube.py`: script that generates the hypercube parameter files.
    Takes a template parameter file (`template_params.yml`) and generates a set
    of new parameter files in the output directory (`params/`).
 2. `setup_runs.py`: script that takes the `.yml` files output by the previous
    script and sets up working directories to run the hypercube simulations.
    Takes various additional arguments: a list of files that need to be copied
    or soft-linked into the run working directories (to create a sandbox for
    every hypercube run), a list of template files that are copied with some
    substitutions (e.g. SLURM scripts where we need to change some names),
    and finally an output file name (e.g. `runs.txt`) that will contain a list
    of all working directories that have been created.
 3. `submit_runs.sh`: reads the list of working directories created by the
    previous script and simply runs an `sbatch` script for each of those (from
    within the corresponding directory). Currently set up to submit VR for the
    final snapshot, but can also be used to submit the hypercube runs
    themselves. To run the hypercube, first use this script to submit the
    hypercube simulations, and then (when the corresponding snapshots exist)
    to run VR on some of the snapshots.
 4. `run_pipeline_0490.sh`: script that can be used to efficiently run the
    pipeline for one of the snapshots of all runs in the hypercube. Can be
    adapted to run on other snapshots as well.
 5. `run_pipeline_CDDF.sh`: script that can be used to efficiently run the
    (very expensive) CDDF script on the two relevant snapshots of a run. Set
    up to be run as a SLURM array job, using `sbatch --array=0-39 SCRIPT`
    (assuming the working directories are indexed from 0 to 39).

After these steps, the scripts in `HypercubePlotter` can be used to further
analyse the hypercube output.

There are 3 additional scripts in this directory:
 - `remove_snaps.sh` can be used to remove snapshots that are not used by the
   analysis (and hence to free up some disk space).
 - `fix_catalogue_names.py` fixed an issue with an early version of one of the
   hypercubes and is mostly meant as an example of how to efficiently deal with
   silly issues.
 - `plot_Ecurve.py` was used to compare the hypercube parameters with some
   early simulation data to assess which range of parameter space the parameters
   were covering. Provided as an example.
