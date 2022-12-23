import numpy as np

# hardcoded size (in bytes) of struct part
part_size = 480

# data types of the variables we care about
part_dtype = [
    ("id", "l"),
    ("gpart", "P"),
    ("x[0]", "d"),
    ("x[1]", "d"),
    ("x[2]", "d"),
    ("v[0]", "f"),
    ("v[1]", "f"),
    ("v[2]", "f"),
    ("a_hydro[0]", "f"),
    ("a_hydro[1]", "f"),
    ("a_hydro[2]", "f"),
    ("mass", "f"),
    ("h", "f"),
    ("u", "f"),
    ("u_dt", "f"),
    ("rho", "f"),
    ("viscosity.div_v", "f"),
    ("viscosity.div_v_dt", "f"),
    ("viscosity.div_v_previous_step", "f"),
    ("viscosity.alpha", "f"),
    ("viscosity.v_sig", "f"),
    ("diffusion.laplace_u", "f"),
    ("diffusion.alpha", "f"),
    ("force.f", "f"),
    ("force.pressure", "f"),
    ("force.soundspeed", "f"),
    ("force.h_dt", "f"),
    ("force.balsara", "f"),
    ("force.alpha_visc_max_ngb", "f"),
]

# size (in bytes) of the variables we care about
defsize = np.dtype(part_dtype).itemsize
# add meaningless bytes to the dtype to account for the other variables
part_dtype.append(("padding", "{0}b".format(part_size - defsize)))


# hardcoded size (in bytes) of struct xpart
xpart_size = 192

# data types of the variables we care about
xpart_dtype = [
    ("x_diff[0]", "f"),
    ("x_diff[1]", "f"),
    ("x_diff[2]", "f"),
    ("x_diff_sort[0]", "f"),
    ("x_diff_sort[1]", "f"),
    ("x_diff_sort[2]", "f"),
    ("v_full[0]", "f"),
    ("v_full[1]", "f"),
    ("v_full[2]", "f"),
    ("a_grav[0]", "f"),
    ("a_grav[1]", "f"),
    ("a_grav[2]", "f"),
    ("u_full", "f"),
    ("split_data.padding_begin", "4b"),
    ("split_data.progrenitor_id", "l"),  # 8 8
    ("split_data.split_tree", "l"),  # 8 16
    ("split_data.split_count", "B"),  # 1 17
    ("split_data.padding_end", "7b"),  # 24 - 17
    ("cooling_data.radiated_energy", "f"),
    ("tracers_data.padding_begin", "4b"),
    ("tracers_data.maximum_temperature", "f"),  # 4 4
    ("tracers_data.stellar_wind_momentum_received", "f"),  # 4 8
    ("tracers_data.nHI_over_nH", "f"),  # 4 12
    ("tracers_data.nHII_over_nH", "f"),  # 4 16
    ("tracers_data.nH2_over_nH", "f"),  # 4 20
    ("tracers_data.HIIregion_timer_gas", "f"),  # 4 24
    ("tracers_data.HIIregion_starid", "l"),  # 8 32
    ("tracers_data.maximum_temperature_scale_factor", "f"),  # 4 36
    ("tracers_data.last_stellar_wind_kick_scale_factor", "f"),  # 4 40
    ("tracers_data.last_SNII_thermal_injection_scale_factor", "f"),  # 4 44
    ("tracers_data.last_SNII_kick_scale_factor", "f"),  # 4 48
    ("tracers_data.last_SNIa_thermal_injection_scale_factor", "f"),  # 4 52
    ("tracers_data.last_AGN_injection_scale_factor", "f"),  # 4 56
    ("tracers_data.density_at_last_SNII_thermal_feedback_event", "f"),  # 4 60
    ("tracers_data.density_at_last_AGN_feedback_event", "f"),  # 4 64
    ("tracers_data.AGN_feedback_energy", "f"),  # 4 68
    ("tracers_data.last_SNII_kick_velocity", "f"),  # 4 72
    ("tracers_data.max_SNII_kick_velocity", "f"),  # 4 76
    ("tracers_data.padding_end", "4b"),  # 80 - 76
    ("sf_data.SFR", "f"),
]

# size (in bytes) of the variables we care about
defsize = np.dtype(xpart_dtype).itemsize
# add meaningless bytes to the dtype to account for the other variables
xpart_dtype.append(("padding", "{0}b".format(xpart_size - defsize)))


# hardcoded size (in bytes) of struct gpart
gpart_size = 112

# data types of the variables we care about
gpart_dtype = [
    ("id", "l"),
    ("x[0]", "d"),
    ("x[1]", "d"),
    ("x[2]", "d"),
    ("v_full[0]", "f"),
    ("v_full[1]", "f"),
    ("v_full[2]", "f"),
    ("a_grav[0]", "f"),
    ("a_grav[1]", "f"),
    ("a_grav[2]", "f"),
    ("a_grav_mesh[0]", "f"),
    ("a_grav_mesh[1]", "f"),
    ("a_grav_mesh[2]", "f"),
    ("potential", "f"),
    ("potential_mesh", "f"),
    ("mass", "f"),
    ("old_a_grav_norm", "f"),
    ("epsilon", "f"),
    ("fof_data.group_id", "L"),
    ("fof_data.group_size", "L"),
    ("time_bin", "b"),
    ("type", "i"),
]

# size (in bytes) of the variables we care about
defsize = np.dtype(gpart_dtype).itemsize
# add meaningless bytes to the dtype to account for the other variables
gpart_dtype.append(("padding", "{0}b".format(gpart_size - defsize)))

# hardcoded size (in bytes) of struct spart
spart_size = 1568

# data types of the variables we care about
spart_dtype = [
    ("id", "l"),
    ("gpart", "P"),
    ("x", "3d"),
    ("x_diff", "3f"),
    ("x_diff_sort", "3f"),
    ("v", "3f"),
    ("mass", "f"),
    ("h", "f"),
    ("density.wcount", "f"),
    ("density.wcount_dh", "f"),
    ("birth_scale_factor", "f"),
    ("last_enrichment_time", "f"),
    ("mass_init", "f"),
    ("SNII_f_E", "f"),
    ("SNIa_f_E", "f"),
    ("birth_density", "f"),
    ("birth_temperature", "f"),
    ("HIIregion_last_rebuild", "f"),
    ("star_timestep", "f"),
    ("HIIregion_mass_to_ionize", "f"),
    ("HIIregion_mass_in_kernel", "f"),
]

# size (in bytes) of the variables we care about
defsize = np.dtype(spart_dtype).itemsize
# add meaningless bytes to the dtype to account for the other variables
spart_dtype.append(("padding", "{0}b".format(spart_size - defsize)))

# hardcoded size (in bytes) of struct bpart
bpart_size = 1632

# data types of the variables we care about
bpart_dtype = [
    ("id", "l"),
    ("gpart", "P"),
    ("x", "3d"),
    ("x_diff", "3f"),
    ("v", "3f"),
    ("mass", "f"),
    ("mass_at_start_of_step", "f"),
    ("h", "f"),
    ("time_bin", "b"),
    ("density.padding_begin", "3b"),
    ("density.wcount", "f"),
    ("density.wcount_dh", "f"),
    ("formation_scale_factor", "f"),
    ("subgrid_mass", "f"),
]

# size (in bytes) of the variables we care about
defsize = np.dtype(bpart_dtype).itemsize
# add meaningless bytes to the dtype to account for the other variables
bpart_dtype.append(("padding", "{0}b".format(bpart_size - defsize)))


def get_arrays():
    # memory map the part file
    parts = np.memmap("parts.dat", dtype=part_dtype)
    # memory map the xpart file
    xparts = np.memmap("xparts.dat", dtype=xpart_dtype)
    # memory map the gpart file
    gparts = np.memmap("gparts.dat", dtype=gpart_dtype)
    # memory map the spart file
    sparts = np.memmap("sparts.dat", dtype=spart_dtype)
    # memory map the bpart file
    bparts = np.memmap("bparts.dat", dtype=bpart_dtype)

    return parts, xparts, gparts, sparts, bparts


def print_element(array, index=0):
    for q in array.dtype.fields:
        if "padding" in q:
            continue
        print("", q, "", array[index][q], array.dtype[q])


if __name__ == "__main__":
    parts, xparts, gparts, sparts, bparts = get_arrays()

    print("parts:", parts.shape)
    print_element(parts)
    print("xparts:", xparts.shape)
    print_element(xparts)
    print("gparts:", gparts.shape)
    print_element(gparts)
    print("sparts:", sparts.shape)
    print_element(sparts, 400)
    print("bparts:", bparts.shape)
    print_element(bparts)
