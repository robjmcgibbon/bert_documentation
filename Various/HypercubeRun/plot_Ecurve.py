#!/usr/bin/env python3

"""
plot_Ecurve.py

Compare the energy feedback model from the various hypercube parameter files
with some output from an actual simulation to assess parameter space coverage.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pl
import yaml
import glob
from swiftsimio import load
import unyt

pl.rcParams["text.usetex"] = True
pl.rcParams["font.size"] = 15


def feedback_fraction_pressure(P, Ppivot, fmin, fmax, nP):
    return fmin + (fmax - fmin) / (1.0 + (P / Ppivot) ** nP)


snap = load(
    "/snap7/scratch/dp004/dc-vand2/PressureDependentFeedback/COLIBRE_L025N0188_latest_meanP/colibre_2729.hdf5"
)
z = 1.0 / snap.stars.birth_scale_factors.value - 1.0
rho = snap.stars.birth_densities.to("g/cm**3") / unyt.mh.to("g")
T = snap.stars.birth_temperatures.to("K")
P = (rho * T).to("K/cm**3")

ymllist = sorted(glob.glob("params/*.yml"))

Elim = [np.inf, -np.inf]
Ps = np.logspace(1.0, 8.0, 256) * unyt.K / unyt.cm**3
for ymlfile in ymllist:
    with open(ymlfile, "r") as handle:
        ymldict = yaml.safe_load(handle)

    Ppivot = (
        float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_P_0_K_p_cm3"])
        * unyt.K
        / unyt.cm**3
    )
    fmin = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_min"])
    fmax = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_max"])
    SNII_E = float(ymldict["COLIBREFeedback"]["SNII_energy_erg"])
    nP = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_n_P"])

    fs = feedback_fraction_pressure(Ps, Ppivot, fmin, fmax, nP)
    Es = fs * SNII_E
    Elim[0] = min(Elim[0], Es.min())
    Elim[1] = max(Elim[1], Es.max())
    pl.semilogx(Ps, Es)

for ymlfile in ["template_params.yml"]:
    with open(ymlfile, "r") as handle:
        ymldict = yaml.safe_load(handle)

    Ppivot = (
        float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_P_0_K_p_cm3"])
        * unyt.K
        / unyt.cm**3
    )
    fmin = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_min"])
    fmax = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_max"])
    SNII_E = float(ymldict["COLIBREFeedback"]["SNII_energy_erg"])
    nP = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_n_P"])

    fs = feedback_fraction_pressure(Ps, Ppivot, fmin, fmax, nP)
    Es = fs * SNII_E
    Elim[0] = min(Elim[0], Es.min())
    Elim[1] = max(Elim[1], Es.max())
    pl.semilogx(Ps, Es, "k-")

pl.xlabel("Stellar birth pressure (K cm$^{-3}$)")
pl.ylabel("Feedback energy (erg)")

Phist, _ = np.histogram(P, bins=Ps)
Phist /= Ps[1:] - Ps[:-1]
Phist /= Phist.max()
pax = pl.gca().twinx()
pax.loglog(
    0.5 * (Ps[1:] + Ps[:-1]),
    Phist,
    "k-",
    alpha=0.5,
    zorder=-9000,
    label="Birth pressure histogram",
)
pax.set_yticks([])

pl.legend(loc="lower right")
pl.tight_layout()
pl.savefig("energies.png", dpi=300)
pl.close()

P_by_z = {
    "$z < 1$": P[z < 1.0],
    "$1 \leq{} z < 3$": P[(z >= 1.0) & (z < 3)],
    "$z \geq{} 3$": P[z >= 3],
}

fig, ax = pl.subplots(3, 1, sharex=True)

Ebin = np.linspace(Elim[0], Elim[1], 256)
Eval = 0.5 * (Ebin[1:] + Ebin[:-1])
for ymlfile in ymllist:
    with open(ymlfile, "r") as handle:
        ymldict = yaml.safe_load(handle)

    Ppivot = (
        float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_P_0_K_p_cm3"])
        * unyt.K
        / unyt.cm**3
    )
    fmin = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_min"])
    fmax = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_max"])
    SNII_E = float(ymldict["COLIBREFeedback"]["SNII_energy_erg"])
    nP = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_n_P"])

    for iax, zlabel in enumerate(P_by_z):
        thisP = P_by_z[zlabel]
        fs = feedback_fraction_pressure(thisP, Ppivot, fmin, fmax, nP)
        thisE = fs * SNII_E
        histE, _ = np.histogram(thisE, bins=Ebin, density=True)
        ax[iax].plot(Eval, np.cumsum(histE))

for ymlfile in ["template_params.yml"]:
    with open(ymlfile, "r") as handle:
        ymldict = yaml.safe_load(handle)

    Ppivot = (
        float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_P_0_K_p_cm3"])
        * unyt.K
        / unyt.cm**3
    )
    fmin = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_min"])
    fmax = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_max"])
    SNII_E = float(ymldict["COLIBREFeedback"]["SNII_energy_erg"])
    nP = float(ymldict["COLIBREFeedback"]["SNII_energy_fraction_n_P"])

    for iax, zlabel in enumerate(P_by_z):
        thisP = P_by_z[zlabel]
        fs = feedback_fraction_pressure(thisP, Ppivot, fmin, fmax, nP)
        thisE = fs * SNII_E
        histE, _ = np.histogram(thisE, bins=Ebin, density=True)
        ax[iax].plot(Eval, np.cumsum(histE), "k-")

for iax, zlabel in enumerate(P_by_z):
    ax[iax].text(
        0.9, 0.1, zlabel, transform=ax[iax].transAxes, horizontalalignment="right"
    )
for a in ax:
    a.set_yticks([])
    a.set_ylabel("CDF")
ax[-1].set_xlabel("Feedback energy (erg)")
pl.tight_layout()
pl.savefig("Ehist.png", dpi=300)
