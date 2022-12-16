#!/bin/bash

# Start an interactive job on cosma8 using the Virgo allocation
# Request 1 node for 1 hour.

srun -p cosma8 -A dp004 -t 1:00:00 --ntasks=4 --cpus-per-task=32 --pty /bin/bash
