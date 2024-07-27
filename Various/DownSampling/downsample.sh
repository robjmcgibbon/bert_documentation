module purge
module load gnu_comp/11.1.0 openmpi/4.1.1 python/3.10.1

cd /snap8/scratch/dp004/dc-mcgi1/downsample

python /cosma/home/dp004/dc-mcgi1/bert_documentation/Various/DownSampling/downsample_snapshot.py \
    /cosma8/data/dp004/flamingo/Runs/L1000N0900/DMO_FIDUCIAL/snapshots/flamingo_0077/flamingo_0077 \
    flamingo_0077 \
    0.01 \
    0

