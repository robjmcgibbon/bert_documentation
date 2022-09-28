"""
Plots the birth pressure distribution.
"""

import matplotlib.pyplot as plt
import numpy as np
import unyt
import traceback

from unyt import mh

from swiftsimio import load


def plot_birth_pressure_distribution(
    name, output_filename, stylesheet, snapshot_filename
):

    names = [name]

    plt.style.use(stylesheet)

    data = [load(snapshot_filename)]
    number_of_bins = 256

    birth_pressure_bins = unyt.unyt_array(
        np.logspace(1.0, 8.0, number_of_bins), units="K/cm**3"
    )
    log_birth_pressure_bin_width = np.log10(birth_pressure_bins[1].value) - np.log10(
        birth_pressure_bins[0].value
    )
    birth_pressure_centers = 0.5 * (birth_pressure_bins[1:] + birth_pressure_bins[:-1])

    # Begin plotting
    fig, axes = plt.subplots(3, 1, sharex=True, sharey=True)
    axes = axes.flat

    ax_dict = {"$z < 1$": axes[0], "$1 < z < 3$": axes[1], "$z > 3$": axes[2]}

    for label, ax in ax_dict.items():
        ax.loglog()
        ax.text(
            0.025, 1.0 - 0.025 * 3, label, transform=ax.transAxes, ha="left", va="top"
        )

    for color, (snapshot, name) in enumerate(zip(data, names)):

        birth_densities = snapshot.stars.birth_densities.to("g/cm**3") / mh.to("g")
        birth_temperatures = snapshot.stars.birth_temperatures.to("K")
        birth_pressures = (birth_densities * birth_temperatures).to("K/cm**3")
        birth_redshifts = 1 / snapshot.stars.birth_scale_factors.value - 1

        # Segment birth pressures into redshift bins
        birth_pressure_by_redshift = {
            "$z < 1$": birth_pressures[birth_redshifts < 1],
            "$1 < z < 3$": birth_pressures[
                np.logical_and(birth_redshifts > 1, birth_redshifts < 3)
            ],
            "$z > 3$": birth_pressures[birth_redshifts > 3],
        }

        # Total number of stars formed
        Num_of_stars_total = len(birth_redshifts)

        for redshift, ax in ax_dict.items():
            data = birth_pressure_by_redshift[redshift]

            H, _ = np.histogram(data, bins=birth_pressure_bins)
            y_points = H / log_birth_pressure_bin_width / Num_of_stars_total

            ax.plot(birth_pressure_centers, y_points, label=name, color=f"C{color}")

            # Add the median stellar birth-pressure line
            ax.axvline(
                np.median(data),
                color=f"C{color}",
                linestyle="dashed",
                zorder=-10,
                alpha=0.5,
            )

    axes[0].legend(loc="upper right", markerfirst=False)
    axes[2].set_xlabel("Stellar Birth Pressure $P_B/k$ [K cm$^{-3}$]")
    axes[1].set_ylabel("$N_{\\rm bin}$ / d$\\log(P_B/k)$ / $N_{\\rm total}$")

    fig.savefig(output_filename)


if __name__ == "__main__":

    plot_birth_pressure_distribution(
        "Test",
        "test.png",
        "mnras.mplstyle",
        "runs/I01_L25N188_JUNE2022_FID/colibre_2729.hdf5",
    )
