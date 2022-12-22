#!/usr/bin/env python3

"""
create_hypercube.py

Create a hypercube, using swiftemulator.
Model parameters are read from `template_params.yml`. Parameter files for the
various hypercube simulations are written to `params/`.
Takes no arguments; everything is hard-coded below.
"""

from swiftemulator.design import latin
from swiftemulator.io.swift import write_parameter_files
from swiftemulator import ModelSpecification, ModelParameters
import numpy as np

np.random.seed(45)

spec = ModelSpecification(
    number_of_parameters=4,
    parameter_names=[
        "COLIBREFeedback:SNII_energy_fraction_min",
        "COLIBREFeedback:SNII_energy_fraction_max",
        "COLIBREFeedback:SNII_energy_fraction_P_0_K_p_cm3",
        "COLIBREFeedback:SNII_energy_fraction_n_P",
    ],
    parameter_printable_names=[
        "$f_{\\rm E,min}$",
        "$f_{\\rm E,max}$",
        "$P_{\\rm pivot}$",
        "$n_{\\rm P}$",
    ],
    parameter_limits=[
        [0.1, 0.75],
        [2.75, 4.5],
        [3.0, 4.5],
        [-0.0969, 0.9031],  # log10(0.8), log10(8)
    ],
)

number_of_simulations = 40

model_parameters = latin.create_hypercube(
    model_specification=spec,
    number_of_samples=number_of_simulations,
)

model_parameters_for_file = model_parameters.model_parameters.copy()

parameter_transforms = {
    "COLIBREFeedback:SNII_energy_fraction_P_0_K_p_cm3": lambda x: 10.0**x,
    "COLIBREFeedback:SNII_energy_fraction_n_P": lambda x: -(10.0**x),
}

base_parameter_file = "template_params.yml"
output_path = "params/"

write_parameter_files(
    filenames={
        key: output_path + f"{key}.yml"
        for key in model_parameters.model_parameters.keys()
    },
    model_parameters=model_parameters,
    parameter_transforms=parameter_transforms,
    base_parameter_file=base_parameter_file,
)
print("FINISHED")
