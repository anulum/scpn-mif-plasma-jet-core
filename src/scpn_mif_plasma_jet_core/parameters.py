# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma Jet Core — plasma-jet-MIF parameter model

"""Validated parameter objects of a plasma-jet-MIF configuration.

The derived quantities implement standard mechanics and nothing more:
per-jet and total kinetic energy ``E = n m v^2 / 2``. They are rough
consistency instruments with documented applicability bounds
(spherically convergent gun arrays; S. C. Hsu et al., IEEE Trans.
Plasma Sci. 40 (2012) 1287); no claim about any real machine follows
from them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from scpn_mif_plasma_jet_core.errors import DeviceConfigurationError

MIN_JET_COUNT: Final = 2


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class JetArray:
    """Plasma-gun jet array of a plasma-jet-MIF configuration.

    Parameters
    ----------
    jet_count
        Number of plasma guns firing convergent jets; at least two —
        a single jet cannot form a converging liner.
    jet_mass_mg
        Mass per jet in milligrams; strictly positive.
    jet_velocity_km_s
        Jet velocity in kilometres per second; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If the count is below two or a parameter violates its bound.
    """

    jet_count: int
    jet_mass_mg: float
    jet_velocity_km_s: float

    def __post_init__(self) -> None:
        """Validate the jet-array invariants.

        Raises
        ------
        DeviceConfigurationError
            If the count is below two or a parameter violates its
            bound.
        """
        if self.jet_count < MIN_JET_COUNT:
            raise DeviceConfigurationError(
                f"jet_count: must be at least {MIN_JET_COUNT}, got {self.jet_count!r}"
            )
        require_positive("jet_mass_mg", self.jet_mass_mg)
        require_positive("jet_velocity_km_s", self.jet_velocity_km_s)

    def jet_kinetic_energy_kj(self) -> float:
        """Kinetic energy of one validated jet.

        Returns
        -------
        float
            ``E = m v^2 / 2`` in kilojoules.
        """
        mass_kg = self.jet_mass_mg * 1.0e-6
        velocity_m_s = self.jet_velocity_km_s * 1.0e3
        return 0.5 * mass_kg * velocity_m_s**2 / 1.0e3

    def total_kinetic_energy_kj(self) -> float:
        """Total kinetic energy of the validated array.

        Returns
        -------
        float
            ``E = n m v^2 / 2`` in kilojoules.
        """
        return self.jet_count * self.jet_kinetic_energy_kj()
