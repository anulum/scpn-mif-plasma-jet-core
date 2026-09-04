# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma-Jet Core — spherical convergence

"""What a spherically converging liner does to what it encloses.

**The exponent is three, and that is the point.** The two other
magneto-inertial families in this group implode a cylinder, where the
density gain of a convergence ``r_0 / r`` is the area ratio and the
exponent is two. This family implodes a **sphere**: the gain is the volume
ratio ``(r_0 / r)^3``, and the adiabatic temperature follows as
``(r_0 / r)^(3 (gamma - 1))``. The relations look like the cylindrical
ones and are not them, which is exactly why they are written here rather
than borrowed.

Both are conservation laws in their ideal limit and both are upper bounds:
a real implosion radiates, conducts and mixes, and this liner is formed by
discrete jets whose merging is the subject of the filed source rather than
something modelled here.

The non-integer power goes through the shared library's deterministic
kernel, as everywhere else in the group.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import NumericsError
from scpn_reactor_kernels.numerics.transcendental import power

from scpn_mif_plasma_jet_core.errors import DeviceConfigurationError
from scpn_mif_plasma_jet_core.parameters import require_positive

#: Adiabatic index of a monatomic ideal gas.
MONATOMIC_GAMMA: Final = 5.0 / 3.0
#: Spatial dimensions a spherical convergence compresses in. Named rather
#: than written as a literal three, because the whole distinction from the
#: cylindrical families lives in this number.
SPHERICAL_DIMENSIONS: Final = 3.0


def require_convergence_ratio(ratio: float) -> float:
    """Return a convergence ratio strictly greater than one.

    Parameters
    ----------
    ratio
        Ratio of the initial radius to the stagnation radius.

    Returns
    -------
    float
        The validated ratio.

    Raises
    ------
    DeviceConfigurationError
        If the ratio is not strictly greater than one. A liner that does
        not converge compresses nothing.
    """
    value = require_positive("convergence_ratio", ratio)
    if value <= 1.0:
        raise DeviceConfigurationError(
            f"convergence_ratio: must be strictly greater than one, got {value!r}"
        )
    return value


def spherical_density_gain(convergence_ratio: float) -> float:
    """Return the density gain of a spherical convergence.

    Parameters
    ----------
    convergence_ratio
        ``r_0 / r``; strictly greater than one.

    Returns
    -------
    float
        ``(r_0 / r)^3``: the **volume** ratio, not the area ratio a
        cylindrical implosion gives.

    Raises
    ------
    DeviceConfigurationError
        If the ratio is not strictly greater than one.
    """
    ratio = require_convergence_ratio(convergence_ratio)
    return ratio * ratio * ratio


def adiabatic_temperature_gain(
    convergence_ratio: float, adiabatic_index: float = MONATOMIC_GAMMA
) -> float:
    """Return the temperature gain of an adiabatic spherical compression.

    Parameters
    ----------
    convergence_ratio
        ``r_0 / r``; strictly greater than one.
    adiabatic_index
        ``gamma``; strictly greater than one, or the compression would
        not heat.

    Returns
    -------
    float
        ``(r_0 / r)^(3 (gamma - 1))``, through the shared library's
        deterministic power kernel. At ``gamma = 5/3`` the exponent is
        exactly two, where the cylindrical families' is four thirds.

    Raises
    ------
    DeviceConfigurationError
        If the ratio or the index falls outside its bound, or if the
        power leaves the kernel's admissible range; the kernel's refusal
        is re-raised under the device error type with its message.
    """
    ratio = require_convergence_ratio(convergence_ratio)
    index = require_positive("adiabatic_index", adiabatic_index)
    if index <= 1.0:
        raise DeviceConfigurationError(
            f"adiabatic_index: must be strictly greater than one, got {index!r}"
        )
    try:
        return power(ratio, SPHERICAL_DIMENSIONS * (index - 1.0))
    except NumericsError as exc:
        raise DeviceConfigurationError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class StagnationState:
    """What one declared convergence does to the enclosed volume.

    Parameters
    ----------
    convergence_ratio
        ``r_0 / r`` of the declared stagnation radius.
    initial_radius_m, stagnation_radius_m
        The radii the ratio runs between.
    adiabatic_index
        ``gamma`` used for the temperature gain.
    density_gain
        ``(r_0 / r)^3``.
    temperature_gain
        ``(r_0 / r)^(3 (gamma - 1))``.
    stagnation_density_kg_m3
        The liner's shell density raised by the density gain.
    """

    convergence_ratio: float
    initial_radius_m: float
    stagnation_radius_m: float
    adiabatic_index: float
    density_gain: float
    temperature_gain: float
    stagnation_density_kg_m3: float

    def to_record(self) -> dict[str, Any]:
        """Project the state to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "convergence_ratio": self.convergence_ratio,
            "initial_radius_m": self.initial_radius_m,
            "stagnation_radius_m": self.stagnation_radius_m,
            "adiabatic_index": self.adiabatic_index,
            "density_gain": self.density_gain,
            "temperature_gain": self.temperature_gain,
            "stagnation_density_kg_m3": self.stagnation_density_kg_m3,
        }


def stagnation_state(
    initial_radius_m: float,
    initial_density_kg_m3: float,
    convergence_ratio: float,
    adiabatic_index: float = MONATOMIC_GAMMA,
) -> StagnationState:
    """Compose the stagnation state of one declared convergence.

    Parameters
    ----------
    initial_radius_m
        Radius the liner starts converging from; strictly positive.
    initial_density_kg_m3
        Mass density of the liner there; strictly positive.
    convergence_ratio
        ``r_0 / r``; strictly greater than one.
    adiabatic_index
        ``gamma``; strictly greater than one.

    Returns
    -------
    StagnationState
        The composed state.

    Raises
    ------
    DeviceConfigurationError
        If any argument falls outside its bound.
    """
    radius = require_positive("initial_radius_m", initial_radius_m)
    density = require_positive("initial_density_kg_m3", initial_density_kg_m3)
    ratio = require_convergence_ratio(convergence_ratio)
    gain = spherical_density_gain(ratio)
    return StagnationState(
        convergence_ratio=ratio,
        initial_radius_m=radius,
        stagnation_radius_m=radius / ratio,
        adiabatic_index=adiabatic_index,
        density_gain=gain,
        temperature_gain=adiabatic_temperature_gain(ratio, adiabatic_index),
        stagnation_density_kg_m3=density * gain,
    )
