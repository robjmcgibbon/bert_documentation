This directory contains two scripts that can be used to do something incredibly brave: read a 
SWIFT restart dump and even change some values in it. This is all very complicated stuff that 
requires detailed knowledge of the layout of SWIFT structs, which means the scripts are 
probably long outdated. They are hence only useful as an example of how to go about this.

The scripts are:
 - `read_restart_file.py`: script that at some point was able to read the values of particle
   variables from the restart file.
 - `new_read_restart_file.py`: somewhat simpler script that at some point was
   used to make a change to a variable in a copy of a restart file. Not quite
   sure what was changed, since the script does not actually contain that
   information anymore.

What both scripts try to illustrate is that doing this kind of thing requires the `struct` 
module, which can convert binary input into a tuple of typed values, if you happen to know the 
binary layout of the binary input. This requires all kinds of weird format strings and is 
complicated by the fact that the compiler sometimes aligns variables, making the binary size of 
structs longer than expected.

To create a binary format string, you will need to look at the SWIFT source code. It can also 
help (a lot) if you have access to a core dump or a debug session of the executable that 
produced the restart file, since that allows you to print the offset and size of variables, 
e.g.:

```
gdb> p sizeof(part.x[0])
8
gdb> p part.v - &part
24
```

`sizeof()` tells you the size (in bytes) of a variable. Pointer arithmetics tells you the 
offset (in bytes) between the position where a variable is stored and the start of the struct. 
By manually adding up sizes and comparing to the reported offsets, you can figure out where 
extra bits are added as padding. Printing variables in `gdb` and comparing with the output you 
get from a script will tell you if your calculations were right.
