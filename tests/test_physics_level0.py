# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma-Jet Core — level-0 record tests

"""The composed level-0 record: identity, canonicity and its non-claims."""

from __future__ import annotations

import hashlib
import json

import pytest
from physics_fixtures import (
    ANCHOR_ENERGY_TOLERANCE,
    ANCHOR_JET_COUNT,
    ANCHOR_TOTAL_KINETIC_ENERGY_KJ,
    anchor_configuration,
    anchor_inputs,
    reference_configuration,
    reference_inputs,
)

from scpn_mif_plasma_jet_core.errors import DeviceConfigurationError
from scpn_mif_plasma_jet_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    Level0Physics,
    level0_physics,
)


def reference_record() -> Level0Physics:
    """Build the synthetic reference level-0 record."""
    return level0_physics(reference_configuration(), reference_inputs(), 10.0)


def test_the_record_is_schema_tagged_and_states_its_non_claims() -> None:
    """The record names its schema and carries the non-claims verbatim."""
    record = reference_record().to_record()
    assert record["schema"] == LEVEL0_SCHEMA
    assert record["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert record["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert list(record) == [
        "schema",
        "schema_version",
        "configuration_digest_sha256",
        "inputs",
        "array",
        "stagnation",
        "non_claims",
    ]


def test_the_non_claims_disown_the_merging_and_the_coverage_map() -> None:
    """The subject of the filed source is what this package does not do."""
    joined = " ".join(LEVEL0_NON_CLAIMS)
    assert "merging of discrete jets" in joined
    assert "not a coverage map" in joined
    assert "upper bounds" in joined


def test_the_record_carries_the_declared_inputs() -> None:
    """The two declared inputs reach the record under their own names."""
    assert reference_record().to_record()["inputs"] == {
        "jet_radius_m": 0.04,
        "launch_radius_m": 0.8,
    }


def test_the_record_binds_the_configuration_it_was_built_from() -> None:
    """The record carries the digest of its own configuration."""
    configuration = reference_configuration()
    record = level0_physics(configuration, reference_inputs(), 10.0)
    assert record.configuration_digest_sha256 == configuration.digest_sha256()


def test_the_stagnation_starts_from_the_launch_radius_and_shell_density() -> None:
    """The two halves of the record agree on where the implosion starts."""
    record = reference_record()
    assert record.stagnation.initial_radius_m == record.inputs.launch_radius_m
    assert record.stagnation.stagnation_density_kg_m3 == (
        record.array.shell_mass_density_kg_m3 * record.stagnation.density_gain
    )


def test_canonical_bytes_are_already_in_canonical_form() -> None:
    """Re-canonicalising the bytes is a no-op, and they round-trip."""
    record = reference_record()
    data = record.canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert decoded == record.to_record()
    assert list(decoded) == sorted(decoded)
    again = json.dumps(decoded, sort_keys=True, separators=(",", ":"))
    assert data == (again + "\n").encode("utf-8")
    assert record.digest_sha256() == hashlib.sha256(data).hexdigest()


def test_the_digest_is_stable_and_moves_with_the_convergence() -> None:
    """The same inputs give the same bytes; a different ratio does not."""
    assert reference_record().digest_sha256() == reference_record().digest_sha256()
    other = level0_physics(reference_configuration(), reference_inputs(), 12.0)
    assert other.digest_sha256() != reference_record().digest_sha256()


def test_a_convergence_that_does_not_compress_is_refused() -> None:
    """The composed record applies the ratio contract before building."""
    with pytest.raises(DeviceConfigurationError, match="convergence_ratio"):
        level0_physics(reference_configuration(), reference_inputs(), 1.0)


def test_the_anchor_record_carries_the_printed_array() -> None:
    """The printed count and total energy are recoverable from the record."""
    record = level0_physics(anchor_configuration(), anchor_inputs(), 10.0).to_record()
    assert record["array"]["jet_count"] == ANCHOR_JET_COUNT
    printed = ANCHOR_TOTAL_KINETIC_ENERGY_KJ * 1.0e3
    got = record["array"]["total_kinetic_energy_j"]
    assert abs(got - printed) / printed < ANCHOR_ENERGY_TOLERANCE
