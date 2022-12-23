Scripts that can be used to automatically compile SWIFT. Some of these have not
been used in a long time and are only provided as example.

Scripts that are still useful:
 - `winkel_compile.py`: compilation script I use to compile SWIFT on my STRW
   desktop (winkel). Automatically loads the right modules, stores the SWIFT
   configuration command as a list (very easy to enable/disable options), has
   additional command line arguments that make it easier to reconfigure, run
   unit tests or change the number of threads used for compilation. Requires
 - `get_module_environment.py`: this script fetches the environment variables
   that are set by loading a given list of modules. In standalone mode, it
   simply prints the environment. When called from another script, it returns
   this environment in a format that can be passed on to `subprocess.run(env=)`.
   Requires
 - `dump_environment.py`: script that simply fetches all environment variables
   and prints them to the standard output.

The remaining four scripts:
 - `clone.py`
 - `compile.py`
 - `simulation.py`
 - `setup_runs.py`
used to be part of some semi-automatic workflow that I used a lot when running
scaling tests. I can probably still retrieve some relevant examples from cosma.
The key point here is that these scripts allow you to quickly set up and submit
a run matrix where different versions of SWIFT can be used with different
configurations etc. to run a number of simulations with possible parameter
variations.
