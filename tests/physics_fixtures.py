# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma-Jet Core — level-0 physics fixtures

"""Fixtures of the level-0 physics tests: one synthetic, one anchored.

The **reference** pair is synthetic and describes nothing.

The **anchor** pair is the PLX array of S. C. Hsu et al.,
arXiv:1201.1879 (2012), which prints 30 jets at 50 km/s, a total liner
mass of 300 mg, a total kinetic energy of 376 kJ, a jet radius of 5 cm and
a vacuum chamber 3 m across.

**The per-jet mass is derived, not printed**, and it follows exactly from
two printed numbers: 300 mg over 30 jets is 10 mg, and that division is
exact in binary.

**The array carries its own consistency check.** Half the printed total
mass times the printed velocity squared is 375.0 kJ against the printed
376 kJ — 0.27 %. The source rounds its energy to three figures, so the
anchor test sits at half a per cent and says why rather than asserting
equality.

**A third printed number pins the one value that had to be declared.**
The source does not print the radius the jets are launched from, only the
chamber. But it prints an initial mass density of 6.63e-4 kg/m^3, and the
radius at which the printed total mass spread over a shell one printed jet
diameter thick gives exactly that density is 0.60 m — inside the printed
chamber. The launch radius is declared as that, and a test asserts the
density it reproduces.

Reproducing a printed value is an anchor, never a claim about that
machine.
"""

from __future__ import annotations

from scpn_mif_plasma_jet_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_mif_plasma_jet_core.parameters import JetArray
from scpn_mif_plasma_jet_core.physics import ArrayInputs

REGISTRY = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)

#: Printed by Hsu et al.: 30 jets at 50 km/s.
ANCHOR_JET_COUNT = 30
ANCHOR_JET_VELOCITY_KM_S = 50.0
#: Printed: the total liner mass and the total kinetic energy.
ANCHOR_TOTAL_MASS_MG = 300.0
ANCHOR_TOTAL_KINETIC_ENERGY_KJ = 376.0
#: Derived exactly from the two printed numbers above.
ANCHOR_JET_MASS_MG = ANCHOR_TOTAL_MASS_MG / ANCHOR_JET_COUNT
#: Printed: the jet radius and the vacuum chamber diameter.
ANCHOR_JET_RADIUS_M = 0.05
ANCHOR_CHAMBER_DIAMETER_M = 3.0
#: Printed: the initial mass density of the liner.
ANCHOR_INITIAL_DENSITY_KG_M3 = 6.63e-4
#: Declared, but not arbitrarily. The source prints the chamber and not
#: the sphere the jets are launched from, so a value has to be chosen —
#: and this one is the radius at which the printed total mass, spread over
#: a shell one printed jet diameter thick, gives the printed initial
#: density. It reproduces that density to 0.02 %, and it sits inside the
#: printed chamber. See the density cross-check in the array tests.
ANCHOR_LAUNCH_RADIUS_M = 0.6
#: The source rounds its energy to three figures and prints no per-jet
#: mass, so the energy anchor is asserted at half a per cent. Measured
#: agreement is 0.27 %.
ANCHOR_ENERGY_TOLERANCE = 0.005


def reference_configuration() -> DeviceConfiguration:
    """Build the synthetic reference configuration.

    Returns
    -------
    DeviceConfiguration
        A validated configuration whose numbers are round.
    """
    return DeviceConfiguration(
        identifier="plasma_jet_mif",
        jets=JetArray(jet_count=12, jet_mass_mg=8.0, jet_velocity_km_s=40.0),
        registry=REGISTRY,
    )


def reference_inputs() -> ArrayInputs:
    """Build the synthetic reference declared inputs.

    Returns
    -------
    ArrayInputs
        Round declared inputs for the reference configuration.
    """
    return ArrayInputs(jet_radius_m=0.04, launch_radius_m=0.8)


def anchor_configuration() -> DeviceConfiguration:
    """Build the configuration of the printed PLX array.

    Returns
    -------
    DeviceConfiguration
        A validated configuration carrying the printed count and speed
        and the per-jet mass the printed totals give.
    """
    return DeviceConfiguration(
        identifier="plasma_jet_mif",
        jets=JetArray(
            jet_count=ANCHOR_JET_COUNT,
            jet_mass_mg=ANCHOR_JET_MASS_MG,
            jet_velocity_km_s=ANCHOR_JET_VELOCITY_KM_S,
        ),
        registry=REGISTRY,
    )


def anchor_inputs() -> ArrayInputs:
    """Build the declared inputs of the anchored array.

    Returns
    -------
    ArrayInputs
        The printed jet radius and a declared launch radius inside the
        printed chamber.
    """
    return ArrayInputs(
        jet_radius_m=ANCHOR_JET_RADIUS_M,
        launch_radius_m=ANCHOR_LAUNCH_RADIUS_M,
    )
