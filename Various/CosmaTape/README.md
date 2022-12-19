This directory contains two scripts that can (somewhat) be used to find files
that were backed up on tape on COSMA, and to compare files on disk and files
on tape:
 - `check_snapshot.py`: Checks if a subset of the L1000N1800 FLAMINGO snapshots
   can be found on tape, by running the same `find` command on tape and on disk.
 - `compare_disk_type`: Compare the file lists output by the above script to
   find missing files.

Note that the first script relies on the fact that files on tape and on disk
use the same path, which is not necessarily true. Files on tape will be stored
using the path that they had when they were written to tape. If that path was
later changed by moving them, the tape path will no longer be correct (although
the tape path can be edited afterwards). The example script will therefore fail
on some of the DMO runs, which are taped under a different directory (but do
exist).
