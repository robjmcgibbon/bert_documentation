#!/bin/bash

# Run an `sbatch` command for all runs in `runs.txt`,
# where `runs.txt` is the output of `setup_runs.py`.

for run in $(cat runs.txt)
do
  cd $run
  sbatch submit_VR_2729.slurm
done
