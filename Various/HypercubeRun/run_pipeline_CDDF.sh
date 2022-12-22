#! /bin/bash
#SBATCH --ntasks 1
#SBATCH --cpus-per-task=28
#SBATCH -J Hypercube-CDDF
#SBATCH -o jobCDDF.%J.out
#SBATCH -e jobCDDF.%J.err
#SBATCH -p cosma7
#SBATCH -A dp203
#SBATCH -t 06:00:00

# Job script used to efficiently run the expensive CDDF plotting script on
# 2 of the hypercube run snapshots
# Should be run as a job array, using `sbatch --array=0-39`.

run=/snap7/scratch/dp004/dc-vand2/PressureDependentFeedback/Hypercube2/wdir_$SLURM_ARRAY_TASK_ID

../pipeline_env/bin/python3 \
    ../pipeline-configs/colibre/scripts/column_density_distribution_function.py \
    -C ../pipeline-configs/colibre \
    -c halos_0490.properties.0 \
    -s colibre_0490.hdf5 \
    -d $run \
    -o $run/pipeline_output_0490 \
    -n Hypercube-z2p5

../pipeline_env/bin/python3 \
    ../pipeline-configs/colibre/scripts/column_density_distribution_function.py \
    -C ../pipeline-configs/colibre \
    -c halos_2729.properties.0 \
    -s colibre_2729.hdf5 \
    -d $run \
    -o $run/pipeline_output_2729 \
    -n Hypercube-z0
