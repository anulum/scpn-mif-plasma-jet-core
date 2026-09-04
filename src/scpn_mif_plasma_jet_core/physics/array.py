# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma-Jet Core — the jet array as a forming liner

"""What an array of discrete jets is, before it becomes a liner.

The configuration carries the array: how many jets, how heavy each is and
how fast it travels. The question the filed source is written about is
whether that array becomes a **spherical** liner, so the relations here are
the ones that bear on it.

**Mass and energy.** The array's mass and kinetic energy are sums, and the
configuration already computes them.

**How much of the sphere the jets actually cover.** A jet of radius
``r_jet`` launched from a radius ``R`` subtends a half-angle
``theta = arcsin(r_jet / R)`` at the centre, so it covers a spherical cap
of solid angle ``2 pi (1 - cos theta)``. ``N`` such caps cover a fraction
``N (1 - cos theta) / 2`` of the sphere. Below one the jets have not met;
at and above one they overlap somewhere, which is what merging into a
liner requires. The fraction is reported, not judged: caps on a sphere
cannot tile it, so a fraction above one does not mean uniform coverage and
this module never says it does.

**Ram pressure.** A converging shell of mass density ``rho`` at speed
``v`` delivers ``rho v^2`` where it stagnates. That is the elementary ram
pressure and nothing more; no equation of state and no shock structure is
modelled.

Reference for the arrangement and the anchor: S. C. Hsu et al.,
arXiv:1201.1879 (2012), which prints the PLX jet array and its totals.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final

from scpn_mif_plasma_jet_core.configuration import DeviceConfiguration
from scpn_mif_plasma_jet_core.errors import DeviceConfigurationError
from scpn_mif_plasma_jet_core.parameters import require_positive

#: Milligrams per kilogram, and metres per kilometre; the configuration
#: declares its array in milligrams and kilometres per second.
MG_PER_KG: Final = 1.0e-6
M_PER_KM: Final = 1.0e3


@dataclass(frozen=True, slots=True)
class ArrayInputs:
    """Declared inputs the configuration does not carry.

    Parameters
    ----------
    jet_radius_m
        Radius of one jet where it is launched; strictly positive.
    launch_radius_m
        Radius of the sphere the jets are launched from; strictly
        positive and strictly larger than the jet radius, or a jet would
        not fit on the sphere it starts from.

    Raises
    ------
    DeviceConfigurationError
        If either input is non-finite or not strictly positive, or if the
        jet does not fit on its launch sphere.
    """

    jet_radius_m: float
    launch_radius_m: float

    def __post_init__(self) -> None:
        """Validate both declared inputs.

        Raises
        ------
        DeviceConfigurationError
            If either input is outside its domain, or the jet does not
            fit on its launch sphere.
        """
        require_positive("jet_radius_m", self.jet_radius_m)
        require_positive("launch_radius_m", self.launch_radius_m)
        if self.jet_radius_m >= self.launch_radius_m:
            raise DeviceConfigurationError(
                "jet_radius_m: must be strictly smaller than launch_radius_m "
                f"({self.jet_radius_m!r} >= {self.launch_radius_m!r})"
            )

    def to_record(self) -> dict[str, float]:
        """Project the inputs to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            One key per declared input.
        """
        return {
            "jet_radius_m": self.jet_radius_m,
            "launch_radius_m": self.launch_radius_m,
        }


def jet_half_angle_rad(jet_radius_m: float, launch_radius_m: float) -> float:
    """Return the half-angle one jet subtends at the centre.

    Parameters
    ----------
    jet_radius_m
        Radius of the jet; strictly positive and smaller than the launch
        radius.
    launch_radius_m
        Radius of the launch sphere; strictly positive.

    Returns
    -------
    float
        ``arcsin(r_jet / R)`` in radian.

    Raises
    ------
    DeviceConfigurationError
        If either argument is outside its domain, or the ratio is not
        strictly below one.
    """
    jet = require_positive("jet_radius_m", jet_radius_m)
    launch = require_positive("launch_radius_m", launch_radius_m)
    if jet >= launch:
        raise DeviceConfigurationError(
            "jet_radius_m: must be strictly smaller than launch_radius_m "
            f"({jet!r} >= {launch!r})"
        )
    return math.asin(jet / launch)


def solid_angle_coverage(
    jet_count: int, jet_radius_m: float, launch_radius_m: float
) -> float:
    """Return the fraction of the sphere the jet caps add up to.

    Parameters
    ----------
    jet_count
        Number of jets; at least one.
    jet_radius_m, launch_radius_m
        Jet radius and launch radius.

    Returns
    -------
    float
        ``N (1 - cos theta) / 2``. This is a **sum of cap areas over the
        sphere's area**, not a coverage map: caps cannot tile a sphere, so
        a value above one means the caps overlap somewhere and says
        nothing about whether any point is left bare.

    Raises
    ------
    DeviceConfigurationError
        If the count is below one or a radius is outside its domain.
    """
    if isinstance(jet_count, bool) or jet_count < 1:
        raise DeviceConfigurationError(
            f"jet_count: must be at least one, got {jet_count!r}"
        )
    half_angle = jet_half_angle_rad(jet_radius_m, launch_radius_m)
    return jet_count * (1.0 - math.cos(half_angle)) / 2.0


def ram_pressure_pa(mass_density_kg_m3: float, speed_m_s: float) -> float:
    """Return the ram pressure of a flow.

    Parameters
    ----------
    mass_density_kg_m3
        Mass density; strictly positive.
    speed_m_s
        Speed; strictly positive.

    Returns
    -------
    float
        ``rho v^2`` in pascal. The elementary ram pressure: no equation of
        state and no shock structure is modelled.

    Raises
    ------
    DeviceConfigurationError
        If either argument is non-finite or not strictly positive.
    """
    density = require_positive("mass_density_kg_m3", mass_density_kg_m3)
    speed = require_positive("speed_m_s", speed_m_s)
    return density * speed * speed


@dataclass(frozen=True, slots=True)
class ArrayState:
    """The jet array of one configuration, expressed physically.

    Parameters
    ----------
    jet_count
        Number of jets, from the configuration.
    jet_mass_kg, total_mass_kg
        One jet's mass and the array's, in SI.
    jet_speed_m_s
        Jet speed, in SI.
    jet_kinetic_energy_j, total_kinetic_energy_j
        One jet's kinetic energy and the array's.
    jet_half_angle_rad
        The half-angle one jet subtends at the centre.
    solid_angle_coverage
        The fraction of the sphere the caps add up to.
    shell_mass_density_kg_m3
        The array's mass spread over a shell one jet diameter thick at
        the launch radius: a declared idealisation of the liner the jets
        are meant to form, not a simulation of the merging.
    ram_pressure_pa
        ``rho v^2`` at that density and the jet speed.
    """

    jet_count: int
    jet_mass_kg: float
    total_mass_kg: float
    jet_speed_m_s: float
    jet_kinetic_energy_j: float
    total_kinetic_energy_j: float
    jet_half_angle_rad: float
    solid_angle_coverage: float
    shell_mass_density_kg_m3: float
    ram_pressure_pa: float

    def to_record(self) -> dict[str, Any]:
        """Project the state to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "jet_count": self.jet_count,
            "jet_mass_kg": self.jet_mass_kg,
            "total_mass_kg": self.total_mass_kg,
            "jet_speed_m_s": self.jet_speed_m_s,
            "jet_kinetic_energy_j": self.jet_kinetic_energy_j,
            "total_kinetic_energy_j": self.total_kinetic_energy_j,
            "jet_half_angle_rad": self.jet_half_angle_rad,
            "solid_angle_coverage": self.solid_angle_coverage,
            "shell_mass_density_kg_m3": self.shell_mass_density_kg_m3,
            "ram_pressure_pa": self.ram_pressure_pa,
        }


def array_state(configuration: DeviceConfiguration, inputs: ArrayInputs) -> ArrayState:
    """Compose the array state of one validated configuration.

    Parameters
    ----------
    configuration
        Validated configuration; its jet array supplies the count, the
        mass and the speed.
    inputs
        Declared jet radius and launch radius.

    Returns
    -------
    ArrayState
        The composed state.

    Raises
    ------
    DeviceConfigurationError
        If a declared input falls outside its bound; the refusals name
        the field.
    """
    jets = configuration.jets
    jet_mass = jets.jet_mass_mg * MG_PER_KG
    speed = jets.jet_velocity_km_s * M_PER_KM
    total_mass = jets.jet_count * jet_mass
    shell_volume = 4.0 * math.pi * inputs.launch_radius_m**2 * 2.0 * inputs.jet_radius_m
    density = total_mass / shell_volume
    return ArrayState(
        jet_count=jets.jet_count,
        jet_mass_kg=jet_mass,
        total_mass_kg=total_mass,
        jet_speed_m_s=speed,
        jet_kinetic_energy_j=jets.jet_kinetic_energy_kj() * 1.0e3,
        total_kinetic_energy_j=jets.total_kinetic_energy_kj() * 1.0e3,
        jet_half_angle_rad=jet_half_angle_rad(
            inputs.jet_radius_m, inputs.launch_radius_m
        ),
        solid_angle_coverage=solid_angle_coverage(
            jets.jet_count, inputs.jet_radius_m, inputs.launch_radius_m
        ),
        shell_mass_density_kg_m3=density,
        ram_pressure_pa=ram_pressure_pa(density, speed),
    )
