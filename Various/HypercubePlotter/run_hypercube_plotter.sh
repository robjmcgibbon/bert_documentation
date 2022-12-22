#!/bin/bash

# Run hypercube-plotter using the configuration and input from this directory
# (pre-processing required; see README).
# The `-l` argument can be used to only produce a single plot, instead of all
# the plots in `hypercube_plots.yml`. This is useful for debugging.

build_env/bin/python3 hypercube-plotter/hypercube-plotter/hyperplotter.py \
  -p hypercube_params/ \
  -c hypercube_config.yml \
  -i hypercube_plots.yml \
  -d hypercube_data/ \
  -o hypercube_output/ \
#  -l stellar_mass_with_scatter_passive_fraction_50
