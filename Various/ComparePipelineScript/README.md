Some scripts used to run a pipeline script on a (large) set of runs and
generate a web page comparing the different plots.

Files:
 - `birth_pressure_distribution.py`: early version of a pipeline script with
   the same name, showing how to adapt an existing pipeline script for use
   with the next script,
 - `plot_runs.py`: that runs the script on every run in the `runs` folder and
   produces a corresponding plot
 - `make_webpage.py`: script that turns the plots into a web page for easy
   comparison

`plot_runs.py` assumes that the `runs` folder in the current working directory
contains a separate folder for each run, with each of these folders containing
one or more snapshots. The script generates a plot for the last snapshot in
each folder and saves it as an image with a filename based on the name of the
folder. Note that `runs` can also be a soft link to a folder, e.g. the folder
where someone else stores all their run output.

`make_webpage.py` simply detects all image files in the current working
directory and adds them to a web page. The web page is generated in the folder
`webpage`. The script creates the folder if it does not exist and copies the
image files into it.
