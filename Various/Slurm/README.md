Scripts that help using SLURM on cosma.

 - `attach_to_job.sh`: attach a terminal to an already running job. Useful to
run `top` to monitor the resource usage of a running job.
 - `smart_pmstat.py`: wrapper around `pmstat` that automatically retrieves the
node names for a job and runs `pmstat` for those.
 - `smart_qstat.py`: wrapper around `squeue` (`qstat` is the name of the PBS
Torque equivalent of `squeue`) that makes the output more useful (e.g. by not
cutting off the job names at a number of characters that is too small to be
useful).
 - `start_interactive_job.sh`: script that contains the working `srun` command
to start an interactive job (cosma8 version).
