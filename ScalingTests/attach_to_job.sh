#! /bin/bash

# Attach a bash process to an already running job
# Usage:
#  ./attach_to_job.sh JOBID
#
# Note that only the owner of the job is allowed to do this.

srun --overlap --pty --jobid $1 /bin/bash
