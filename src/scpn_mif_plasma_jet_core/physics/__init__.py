# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma-Jet Core — level-0 device physics package

"""Level-0 device physics of the plasma-jet magneto-inertial family.

Two closed forms on the validated configuration: the jet array as a
forming liner — its mass and energy, the fraction of the sphere its jets
add up to, and the ram pressure of the shell they are meant to form — and
what a **spherical** convergence does to what it encloses, where the
density gain is the volume ratio and not the area ratio the cylindrical
families use. Both compressions are ideal limits recorded as upper bounds,
and the merging of the jets is not modelled. Design record: ADR 0005.
"""

from __future__ import annotations

from scpn_mif_plasma_jet_core.physics.array import (
    M_PER_KM,
    MG_PER_KG,
    ArrayInputs,
    ArrayState,
    array_state,
    jet_half_angle_rad,
    ram_pressure_pa,
    solid_angle_coverage,
)
from scpn_mif_plasma_jet_core.physics.convergence import (
    MONATOMIC_GAMMA,
    SPHERICAL_DIMENSIONS,
    StagnationState,
    adiabatic_temperature_gain,
    require_convergence_ratio,
    spherical_density_gain,
    stagnation_state,
)
from scpn_mif_plasma_jet_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    Level0Physics,
    level0_physics,
)

__all__ = [
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MG_PER_KG",
    "MONATOMIC_GAMMA",
    "M_PER_KM",
    "SPHERICAL_DIMENSIONS",
    "ArrayInputs",
    "ArrayState",
    "Level0Physics",
    "StagnationState",
    "adiabatic_temperature_gain",
    "array_state",
    "jet_half_angle_rad",
    "level0_physics",
    "ram_pressure_pa",
    "require_convergence_ratio",
    "solid_angle_coverage",
    "spherical_density_gain",
    "stagnation_state",
]
