#! /bin/bash

# Start another bash terminal running inside the allocation of an already
# running job.
# Note that there is no way to control on which node of a multi-node job this
# bash instance will run.

srun --overlap --pty --jobid $1 /bin/bash
