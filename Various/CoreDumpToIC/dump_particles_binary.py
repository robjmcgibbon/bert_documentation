import subprocess
import time

nr_parts = 52842625
parts_addr = 0x2B236400F480
part_size = 480
xparts_addr = 0x2B2964010500
xpart_size = 192
nr_gparts = 106314397
gparts_addr = 0x2B2BE4011580
gpart_size = 112
nr_sparts = 721450
sparts_addr = 0x2B35C4D38000
spart_size = 1568
nr_bparts = 2667
bparts_addr = 0x2B306B443580
bpart_size = 1632

swift = "/snap7/scratch/dp004/dc-chai1/swift/swift-colibre_MAY6_h_optimisation_v3_CFLAGS_SUBTASKS_VAR_SN_dT_UNOPTIMISED_NAN_CHECK/examples/swift"
core = "/snap7/scratch/dp004/dc-chai1/my_cosmological_box/104c3_104b2_norm_0p3_L025N376_unupt/core.158570"

chunksize = 1000000

nchunk = nr_parts // chunksize + ((nr_parts % chunksize) > 0)
for ichunk in range(nchunk):
    ibeg = ichunk * chunksize
    iend = (ichunk + 1) * chunksize
    iend = min(iend, nr_parts)

    cmd = "gdb --batch --quiet"
    cmd += ' --eval-command="dump memory parts{0:04d}.dat {1} {2}"'.format(
        ichunk, parts_addr + ibeg * part_size, parts_addr + iend * part_size
    )
    cmd += " {0} {1}".format(swift, core)
    print(cmd)
    run = subprocess.run(cmd, shell=True, capture_output=True)
    print(run.stderr)

    cmd = "gdb --batch --quiet"
    cmd += ' --eval-command="dump memory xparts{0:04d}.dat {1} {2}"'.format(
        ichunk, xparts_addr + ibeg * xpart_size, xparts_addr + iend * xpart_size
    )
    cmd += " {0} {1}".format(swift, core)
    print(cmd)
    run = subprocess.run(cmd, shell=True, capture_output=True)
    print(run.stderr)

nchunk = nr_gparts // chunksize + ((nr_gparts % chunksize) > 0)
for ichunk in range(nchunk):
    ibeg = ichunk * chunksize
    iend = (ichunk + 1) * chunksize
    iend = min(iend, nr_gparts)

    cmd = "gdb --batch --quiet"
    cmd += ' --eval-command="dump memory gparts{0:04d}.dat {1} {2}"'.format(
        ichunk, gparts_addr + ibeg * gpart_size, gparts_addr + iend * gpart_size
    )
    cmd += " {0} {1}".format(swift, core)
    print(cmd)
    run = subprocess.run(cmd, shell=True, capture_output=True)
    print(run.stderr)

nchunk = nr_sparts // chunksize + ((nr_sparts % chunksize) > 0)
for ichunk in range(nchunk):
    ibeg = ichunk * chunksize
    iend = (ichunk + 1) * chunksize
    iend = min(iend, nr_sparts)

    cmd = "gdb --batch --quiet"
    cmd += ' --eval-command="dump memory sparts{0:04d}.dat {1} {2}"'.format(
        ichunk, sparts_addr + ibeg * spart_size, sparts_addr + iend * spart_size
    )
    cmd += " {0} {1}".format(swift, core)
    print(cmd)
    run = subprocess.run(cmd, shell=True, capture_output=True)
    print(run.stderr)

nchunk = nr_bparts // chunksize + ((nr_bparts % chunksize) > 0)
for ichunk in range(nchunk):
    ibeg = ichunk * chunksize
    iend = (ichunk + 1) * chunksize
    iend = min(iend, nr_bparts)

    cmd = "gdb --batch --quiet"
    cmd += ' --eval-command="dump memory bparts{0:04d}.dat {1} {2}"'.format(
        ichunk, bparts_addr + ibeg * bpart_size, bparts_addr + iend * bpart_size
    )
    cmd += " {0} {1}".format(swift, core)
    print(cmd)
    run = subprocess.run(cmd, shell=True, capture_output=True)
    print(run.stderr)
