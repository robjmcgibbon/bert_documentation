This directory contains three scripts that perform actual magic: they convert a core dump of a 
SWIFT simulation into an HDF5 file that can be used as initial condition for a SWIFT 
simulation. Not particularly useful in itself, but it does illustrate a lot of interesting 
concepts.

The scripts are:
 - `dump_particles_binary.py`: script that is used to retrieve the raw binary
   particle buffers from the core dump. Uses `gdb` to perform a raw memory dump from the core 
   file to a set of binary files. This requires some input: the number of particles of each 
   type, the start address (pointer) of the particle buffer of each type, and the size of each 
   particle struct (as reported by `sizeof()`). All of these can be retrieved from an 
   interactive `gdb` session using the same core dump, if you manage to get access to the 
   `space` struct (which is not always possible).
 - `new_read_particles.py`: script that can read the binary dumps created in the previous step 
   and convert them into a `numpy` array. This requires some memory mapping and `numpy` 
   structured data type magic. Since `gdb` does not like outputting very large particle 
   buffers, the output of the previous script is chunked. This script requires a single input 
   file, which can be obtained by running e.g. `cat parts_*.dat > parts.dat`.
 - `create_IC.py`: script that calls a function in the previous script to get the particle 
   data, and then uses this information to produce a valid SWIFT IC. Definitely the least 
   interesting of the three scripts, but a good example of how the output of the second script 
   can be used for real applications.
