Raw backup of Hypercube folder on /snap7. Needs proper documentation.
Depends on the hypercube-plotter package.

The files in this directory can be used in conjunction with the
hypercube-plotter package (or more specifically, the `hypercube-fixed` branch
of https://github.com/bwvdnbro/hypercube-plotter/tree/hypercube-fixes) to make
pipeline like plots of the results of a (COLIBRE) hypercube.

An emulator is constructed for every plot and trained using the hypercube
results. Then a web page with various types of pages is constructed:
 - pages where all plots are shown, whereby one parameter in the hypercube is
   varied and the others are fixed
 - pages where one plot is shown and the impact of varying all parameters is
   demonstrated
 - pages where the emulator predictions are compared with the actual hypercube
   output for each plot

For this work, we will assume that the working directory has the following
subdirectories:
 - `hypercube_params`: parameter files for the SWIFT simulations that were part
   of the hypercube
 - `hypercube_data`: hypercube simulation results that go into the plots. These
   are the `.yml` outputs from the pipeline and some additional files for plots
   that are created from scripts (see below).
 - `hypercube-plotter`: clone of the hypercube-plotter repository.
 - `hypercube_output`: empty directory in which the resulting web pages (and
   plots) will be stored.

The plots used by hypercube-plotter need to be contained in `.yml` files, like
the ones produced by the pipeline. For plots that do not use the autoplotter
functionality of the pipeline, these `.yml` files do not exist. The following
scripts in this directory can be used to produce them:
 - `convert_gas_evolution.py`: produces `.yml` output for the gas evolution
   plots that show the cosmic HI and H2 density as a function of time.
 - `convert_SFH.py`: produces `.yml` output for the cosmic star formation rate
   plot.

On top of that, we also need the output of the (new) morphology pipeline
(https://github.com/SWIFTSIM/morpholopy), which is also a `.yml` file.

Lastly, all of these `.yml` files need to be combined into a single `.yml` file
per hypercube simulation. This is achieved by running the `produce_yaml.py`
script. This script can also automatically run the morphology pipeline and the
two conversion scripts mentioned above.

Once all of this has been done, `run_hypercube_plotter.sh` can be used to run
hypercube-plotter and produce the images and web pages. This requires some
`.yml` input files that are also given here:
 - `hypercube_config.yml`: hypercube parameters. Very similar to the parameters
   that you need to specify in the hypercube creation script.
 - `hypercube_plots.yml`: parameters of the plots we want to include in the
   output. Every plot contains the necessary input for the plot emulator and
   information required to create the plot and optionally add observational
   data to it.

Plots that do not use the autoplotter usually do not have ready made
observational data either. These plots require custom plotting scripts to add
observational data. That is the purpose of the remaining three scripts in this
directory: `observations_rhoH2.py`, `observations_rhoHI.py`,
`observations_sfh.py`.

More documentation can be found in the script files themselves.
