# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma Jet Core — parameter model tests

"""Every validation branch of the plasma-jet-MIF parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from scpn_mif_plasma_jet_core.errors import DeviceConfigurationError
from scpn_mif_plasma_jet_core.parameters import (
    JetArray,
    require_finite,
    require_positive,
)


def synthetic_array(**overrides: Any) -> JetArray:
    """Build a valid synthetic jet array with optional overrides."""
    values: dict[str, Any] = {
        "jet_count": 36,
        "jet_mass_mg": 2.0,
        "jet_velocity_km_s": 50.0,
    }
    values.update(overrides)
    return JetArray(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_kinetic_energy_formulas() -> None:
    """The kinetic-energy relations follow standard mechanics exactly."""
    array = synthetic_array()
    per_jet = 0.5 * 2.0e-6 * (50.0e3) ** 2 / 1.0e3
    assert array.jet_kinetic_energy_kj() == pytest.approx(per_jet)
    assert array.total_kinetic_energy_kj() == pytest.approx(36 * per_jet)


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"jet_count": 1}, "jet_count"),
        ({"jet_count": 0}, "jet_count"),
        ({"jet_mass_mg": 0.0}, "jet_mass_mg"),
        ({"jet_velocity_km_s": -1.0}, "jet_velocity_km_s"),
        ({"jet_velocity_km_s": math.nan}, "jet_velocity_km_s"),
    ],
)
def test_invalid_array_is_rejected(overrides: dict[str, Any], fragment: str) -> None:
    """Each jet-array violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_array(**overrides)


def test_two_jets_are_representable() -> None:
    """The minimum multi-jet array constructs."""
    assert synthetic_array(jet_count=2).jet_count == 2
