# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma-Jet Core — spherical convergence tests

"""Spherical convergence, and how it differs from a cylindrical one."""

from __future__ import annotations

import math
from collections.abc import Callable

import pytest

from scpn_mif_plasma_jet_core.errors import DeviceConfigurationError
from scpn_mif_plasma_jet_core.physics.convergence import (
    MONATOMIC_GAMMA,
    SPHERICAL_DIMENSIONS,
    adiabatic_temperature_gain,
    spherical_density_gain,
    stagnation_state,
)


def test_the_density_gain_is_the_volume_ratio_not_the_area_ratio() -> None:
    """The exponent is three, and that is what makes this family itself.

    A cylindrical implosion gains the area ratio. This one implodes a
    sphere, so it gains the volume ratio — a factor of the convergence
    larger, and the whole distinction lives in that exponent.
    """
    ratio = 10.0
    assert spherical_density_gain(ratio) == ratio**3
    assert spherical_density_gain(ratio) == ratio * (ratio * ratio)
    assert SPHERICAL_DIMENSIONS == 3.0


def test_the_temperature_gain_is_the_spherical_adiabatic_power() -> None:
    """``(r0/r)^(3(gamma-1))``; at gamma = 5/3 the exponent is exactly two.

    Exactly, and it was measured rather than assumed: ``3 * (5/3 - 1)``
    evaluates to ``2.0`` in binary. The cylindrical families' equivalent,
    ``2 * (5/3 - 1)``, is 1.3333333333333335 and is **not** exactly four
    thirds — so the equality below can be written here and could not be
    written there.
    """
    assert SPHERICAL_DIMENSIONS * (MONATOMIC_GAMMA - 1.0) == 2.0
    assert math.isclose(adiabatic_temperature_gain(7.0), 7.0**2.0, rel_tol=1.0e-12)


def test_the_temperature_gain_uses_the_shared_deterministic_kernel() -> None:
    """The one transcendental goes through the library, not the platform."""
    from scpn_reactor_kernels.numerics.transcendental import power

    assert adiabatic_temperature_gain(6.0) == power(
        6.0, SPHERICAL_DIMENSIONS * (MONATOMIC_GAMMA - 1.0)
    )


def test_a_stronger_convergence_compresses_and_heats_more() -> None:
    """Both gains are monotone in the convergence ratio."""
    assert spherical_density_gain(4.0) < spherical_density_gain(9.0)
    assert adiabatic_temperature_gain(4.0) < adiabatic_temperature_gain(9.0)


@pytest.mark.parametrize("ratio", [1.0, 0.5, 0.0])
def test_every_relation_refuses_a_ratio_that_does_not_converge(ratio: float) -> None:
    """A contract only some of the functions apply is not a contract."""
    calls: tuple[Callable[[], float], ...] = (
        lambda: spherical_density_gain(ratio),
        lambda: adiabatic_temperature_gain(ratio),
    )
    for call in calls:
        with pytest.raises(DeviceConfigurationError, match="convergence_ratio"):
            call()


@pytest.mark.parametrize("index", [1.0, 0.5, 0.0, math.nan])
def test_an_index_that_does_not_heat_is_refused(index: float) -> None:
    """At gamma of one or below, an adiabatic compression does not raise T."""
    with pytest.raises(DeviceConfigurationError, match="adiabatic_index"):
        adiabatic_temperature_gain(10.0, index)


def test_a_power_that_leaves_the_kernel_range_is_re_raised() -> None:
    """The library's refusal reaches the caller as a device error."""
    with pytest.raises(DeviceConfigurationError, match=r"power|exponent"):
        adiabatic_temperature_gain(1.0e6, 1.0e6)


def test_the_state_reports_both_radii_and_raises_the_density() -> None:
    """The record carries the radii the ratio runs between."""
    state = stagnation_state(0.6, 6.63e-4, 10.0)
    assert state.initial_radius_m == 0.6
    assert state.stagnation_radius_m == 0.6 / 10.0
    assert state.density_gain == 1000.0
    assert state.stagnation_density_kg_m3 == 6.63e-4 * 1000.0
    assert state.adiabatic_index == MONATOMIC_GAMMA


@pytest.mark.parametrize(
    ("radius", "density", "field_name"),
    [
        (0.0, 6.63e-4, "initial_radius_m"),
        (0.6, 0.0, "initial_density_kg_m3"),
        (math.inf, 6.63e-4, "initial_radius_m"),
    ],
)
def test_the_state_refuses_each_argument_by_name(
    radius: float, density: float, field_name: str
) -> None:
    """Each refusal names the field that is wrong."""
    with pytest.raises(DeviceConfigurationError, match=field_name):
        stagnation_state(radius, density, 10.0)


def test_the_state_record_keys_are_the_declared_fields() -> None:
    """The record carries one key per field, in declaration order."""
    assert list(stagnation_state(0.6, 6.63e-4, 10.0).to_record()) == [
        "convergence_ratio",
        "initial_radius_m",
        "stagnation_radius_m",
        "adiabatic_index",
        "density_gain",
        "temperature_gain",
        "stagnation_density_kg_m3",
    ]
