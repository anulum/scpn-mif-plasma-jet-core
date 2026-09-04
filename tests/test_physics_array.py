# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma-Jet Core — jet array tests

"""The jet array as a forming liner, on the printed PLX numbers."""

from __future__ import annotations

import math

import pytest
from physics_fixtures import (
    ANCHOR_CHAMBER_DIAMETER_M,
    ANCHOR_ENERGY_TOLERANCE,
    ANCHOR_INITIAL_DENSITY_KG_M3,
    ANCHOR_JET_COUNT,
    ANCHOR_JET_MASS_MG,
    ANCHOR_JET_RADIUS_M,
    ANCHOR_JET_VELOCITY_KM_S,
    ANCHOR_LAUNCH_RADIUS_M,
    ANCHOR_TOTAL_KINETIC_ENERGY_KJ,
    ANCHOR_TOTAL_MASS_MG,
    anchor_configuration,
    anchor_inputs,
    reference_configuration,
    reference_inputs,
)

from scpn_mif_plasma_jet_core.errors import DeviceConfigurationError
from scpn_mif_plasma_jet_core.physics.array import (
    ArrayInputs,
    array_state,
    jet_half_angle_rad,
    ram_pressure_pa,
    solid_angle_coverage,
)


def test_the_half_angle_is_the_closed_form() -> None:
    """A jet of radius r on a sphere of radius R subtends arcsin(r/R)."""
    assert jet_half_angle_rad(0.05, 0.6) == math.asin(0.05 / 0.6)


def test_a_jet_that_does_not_fit_on_its_launch_sphere_is_refused() -> None:
    """A jet as wide as the sphere it starts from is not an arrangement."""
    with pytest.raises(DeviceConfigurationError, match="jet_radius_m"):
        jet_half_angle_rad(0.6, 0.6)


@pytest.mark.parametrize(
    ("jet", "launch", "field_name"),
    [
        (0.0, 0.6, "jet_radius_m"),
        (-1.0, 0.6, "jet_radius_m"),
        (0.05, 0.0, "launch_radius_m"),
        (0.05, math.nan, "launch_radius_m"),
    ],
)
def test_the_half_angle_refuses_each_argument_by_name(
    jet: float, launch: float, field_name: str
) -> None:
    """Each refusal names the field that is wrong."""
    with pytest.raises(DeviceConfigurationError, match=field_name):
        jet_half_angle_rad(jet, launch)


def test_the_coverage_is_the_sum_of_the_cap_areas() -> None:
    """N caps of half-angle theta sum to N (1 - cos theta) / 2 of a sphere."""
    theta = math.asin(0.05 / 0.6)
    assert solid_angle_coverage(30, 0.05, 0.6) == 30 * (1.0 - math.cos(theta)) / 2.0


def test_more_jets_cover_more_and_a_wider_jet_covers_more() -> None:
    """Both are monotone, which is the whole content of the quantity."""
    assert solid_angle_coverage(60, 0.05, 0.6) > solid_angle_coverage(30, 0.05, 0.6)
    assert solid_angle_coverage(30, 0.10, 0.6) > solid_angle_coverage(30, 0.05, 0.6)


@pytest.mark.parametrize("count", [0, -1])
def test_an_array_of_no_jets_is_refused(count: int) -> None:
    """A liner needs at least one jet to be formed from."""
    with pytest.raises(DeviceConfigurationError, match="jet_count"):
        solid_angle_coverage(count, 0.05, 0.6)


def test_a_boolean_jet_count_is_refused() -> None:
    """A boolean is not a count, even though Python says it is an int."""
    boolean_count: int = True
    with pytest.raises(DeviceConfigurationError, match="jet_count"):
        solid_angle_coverage(boolean_count, 0.05, 0.6)


def test_the_ram_pressure_is_the_closed_form() -> None:
    """A converging flow delivers rho v squared where it stagnates."""
    assert ram_pressure_pa(6.63e-4, 50.0e3) == 6.63e-4 * 50.0e3 * 50.0e3


@pytest.mark.parametrize(
    ("density", "speed", "field_name"),
    [
        (0.0, 50.0e3, "mass_density_kg_m3"),
        (6.63e-4, 0.0, "speed_m_s"),
        (math.inf, 50.0e3, "mass_density_kg_m3"),
    ],
)
def test_the_ram_pressure_refuses_each_argument_by_name(
    density: float, speed: float, field_name: str
) -> None:
    """Each refusal names the field that is wrong."""
    with pytest.raises(DeviceConfigurationError, match=field_name):
        ram_pressure_pa(density, speed)


@pytest.mark.parametrize(
    ("jet", "launch", "field_name"),
    [
        (0.0, 0.6, "jet_radius_m"),
        (0.05, 0.0, "launch_radius_m"),
        (0.7, 0.6, "jet_radius_m"),
    ],
)
def test_the_declared_inputs_refuse_each_field_by_name(
    jet: float, launch: float, field_name: str
) -> None:
    """A declared input outside its domain is refused."""
    with pytest.raises(DeviceConfigurationError, match=field_name):
        ArrayInputs(jet_radius_m=jet, launch_radius_m=launch)


def test_the_state_converts_the_configuration_units_to_si() -> None:
    """The configuration is in milligrams and km/s; the relations are SI."""
    configuration = reference_configuration()
    state = array_state(configuration, reference_inputs())
    jets = configuration.jets
    assert state.jet_mass_kg == jets.jet_mass_mg * 1.0e-6
    assert state.jet_speed_m_s == jets.jet_velocity_km_s * 1.0e3
    assert state.total_mass_kg == jets.jet_count * state.jet_mass_kg


def test_the_state_totals_are_the_configuration_totals() -> None:
    """The array's own sums reach the record unchanged, in joules."""
    configuration = reference_configuration()
    state = array_state(configuration, reference_inputs())
    assert state.jet_kinetic_energy_j == (
        configuration.jets.jet_kinetic_energy_kj() * 1.0e3
    )
    assert state.total_kinetic_energy_j == (
        configuration.jets.total_kinetic_energy_kj() * 1.0e3
    )


def test_the_shell_density_spreads_the_mass_over_one_jet_diameter() -> None:
    """The idealised liner is a shell as thick as a jet is wide."""
    inputs = reference_inputs()
    state = array_state(reference_configuration(), inputs)
    volume = 4.0 * math.pi * inputs.launch_radius_m**2 * 2.0 * inputs.jet_radius_m
    assert state.shell_mass_density_kg_m3 == state.total_mass_kg / volume
    assert state.ram_pressure_pa == ram_pressure_pa(
        state.shell_mass_density_kg_m3, state.jet_speed_m_s
    )


def test_the_state_record_keys_are_the_declared_fields() -> None:
    """The record carries one key per field, in declaration order."""
    state = array_state(reference_configuration(), reference_inputs())
    assert list(state.to_record()) == [
        "jet_count",
        "jet_mass_kg",
        "total_mass_kg",
        "jet_speed_m_s",
        "jet_kinetic_energy_j",
        "total_kinetic_energy_j",
        "jet_half_angle_rad",
        "solid_angle_coverage",
        "shell_mass_density_kg_m3",
        "ram_pressure_pa",
    ]


def test_the_per_jet_mass_follows_exactly_from_two_printed_numbers() -> None:
    """300 mg over 30 jets is 10 mg, and that division is exact."""
    assert ANCHOR_JET_MASS_MG == ANCHOR_TOTAL_MASS_MG / ANCHOR_JET_COUNT
    assert ANCHOR_JET_MASS_MG == 10.0


def test_the_anchor_reproduces_the_printed_total_mass_exactly() -> None:
    """The array's mass is the printed liner mass, to the last bit."""
    state = array_state(anchor_configuration(), anchor_inputs())
    assert state.total_mass_kg == ANCHOR_TOTAL_MASS_MG * 1.0e-6


def test_the_anchor_reproduces_the_printed_total_kinetic_energy() -> None:
    """The printed energy comes back out of the printed mass and speed.

    Asserted at half a per cent, not as an equality, and the reason is
    stated: the source rounds its energy to three figures. Measured
    agreement is 0.27 %.
    """
    state = array_state(anchor_configuration(), anchor_inputs())
    printed = ANCHOR_TOTAL_KINETIC_ENERGY_KJ * 1.0e3
    assert math.isclose(
        state.total_kinetic_energy_j, printed, rel_tol=ANCHOR_ENERGY_TOLERANCE
    )


def test_the_declared_launch_radius_reproduces_the_printed_density() -> None:
    """The one value that had to be declared is pinned by a printed one.

    The source prints no launch radius, only the chamber. It does print an
    initial mass density, and the radius at which the printed total mass
    spread over a shell one printed jet diameter thick gives that density
    is what the fixture declares. Reproducing it to better than a tenth of
    a per cent is what makes the declaration more than a guess, and it
    also checks that the shell idealisation matches the source's own.
    """
    state = array_state(anchor_configuration(), anchor_inputs())
    assert math.isclose(
        state.shell_mass_density_kg_m3,
        ANCHOR_INITIAL_DENSITY_KG_M3,
        rel_tol=1.0e-3,
    )
    assert ANCHOR_LAUNCH_RADIUS_M < ANCHOR_CHAMBER_DIAMETER_M / 2.0


def test_the_anchor_carries_the_printed_count_speed_and_jet_radius() -> None:
    """The remaining printed values reach the state unchanged."""
    state = array_state(anchor_configuration(), anchor_inputs())
    assert state.jet_count == ANCHOR_JET_COUNT
    assert state.jet_speed_m_s == ANCHOR_JET_VELOCITY_KM_S * 1.0e3
    assert state.jet_half_angle_rad == math.asin(
        ANCHOR_JET_RADIUS_M / ANCHOR_LAUNCH_RADIUS_M
    )


def test_the_printed_array_does_not_cover_the_sphere() -> None:
    """Thirty jets of five centimetres at sixty do not add up to a sphere.

    Worth asserting rather than assuming: the quantity is a sum of cap
    areas and this array sums to about five per cent, which is why the
    filed source is a study of whether the jets merge into a liner at all
    rather than an assertion that they do.
    """
    state = array_state(anchor_configuration(), anchor_inputs())
    assert 0.0 < state.solid_angle_coverage < 0.1
