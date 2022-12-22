#!/bin/bash

# remove snapshots we don't need for the analysis
# we do not want to remove: 490, 623, 2729

for i in {0000..0489}
do
  rm wdir*/colibre_$i.hdf5
done

for i in {0491..0622}
do
  rm wdir*/colibre_$i.hdf5
done

for i in {0624..2728}
do
  rm wdir*/colibre_$i.hdf5
done
