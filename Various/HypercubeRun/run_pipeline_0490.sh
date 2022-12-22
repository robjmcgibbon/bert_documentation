#!/bin/bash

# Run the pipeline (in parallel) on snapshot 490 for every simulation in the
# hypercube.
# Runs the fast, no plotting mode of the pipeline.
# Runs 16 instances at once using gnu-parallel.

module load gnu-parallel

cat runs.txt | parallel -j 16 \
  ../pipeline_env/bin/swift-pipeline \
    -C ../pipeline-configs/colibre \
    -c halos_0490.properties.0 \
    -s colibre_0490.hdf5 \
    -i {} \
    -o {}/pipeline_output_0490 \
    -j 1 --fast --no-plots
