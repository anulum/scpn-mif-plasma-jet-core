# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma-Jet Core — level-0 physics record

"""Level-0 physics record of one validated plasma-jet configuration.

The record composes the two closed forms this package implements — the jet
array as a forming liner, and what a spherical convergence does to what it
encloses — and serialises canonically with a SHA-256 digest.

The compressions are conservation laws in their ideal limit and are
recorded as upper bounds. The merging of discrete jets into a liner is the
subject of the filed source and is **not** modelled here: this package
reports how much of the sphere the jets add up to, and stops.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_mif_plasma_jet_core.configuration import DeviceConfiguration
from scpn_mif_plasma_jet_core.physics.array import ArrayInputs, ArrayState, array_state
from scpn_mif_plasma_jet_core.physics.convergence import (
    MONATOMIC_GAMMA,
    StagnationState,
    require_convergence_ratio,
    stagnation_state,
)

LEVEL0_SCHEMA: Final = "scpn.plasma-jet-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"
LEVEL0_NON_CLAIMS: Final = (
    (
        "closed-form evaluation of a jet array and of ideal spherical "
        "compression on a declared operating point"
    ),
    "no equation of motion, equation of state or transport equation is solved",
    (
        "the merging of discrete jets into a liner is not modelled; the solid "
        "angle reported is a sum of cap areas, not a coverage map, and says "
        "nothing about whether any point of the sphere is left bare"
    ),
    (
        "the compressed density and temperature are the loss-free limits; both "
        "are upper bounds, never predictions"
    ),
    "no yield, gain, reactivity, confinement or breakeven statement",
    (
        "no value describes or validates any real machine; an anchor reproduces "
        "a number the filed source prints and nothing further"
    ),
)


@dataclass(frozen=True, slots=True)
class Level0Physics:
    """Composed level-0 record of one configuration and its inputs.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the record was built from.
    inputs
        Declared jet radius and launch radius.
    array
        The jet array expressed physically.
    stagnation
        What the declared convergence does to the enclosed volume.
    """

    configuration_digest_sha256: str
    inputs: ArrayInputs
    array: ArrayState
    stagnation: StagnationState

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with its non-claims.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "inputs": self.inputs.to_record(),
            "array": self.array.to_record(),
            "stagnation": self.stagnation.to_record(),
            "non_claims": list(LEVEL0_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def level0_physics(
    configuration: DeviceConfiguration,
    inputs: ArrayInputs,
    convergence_ratio: float,
    adiabatic_index: float = MONATOMIC_GAMMA,
) -> Level0Physics:
    """Compose the level-0 physics record of one validated configuration.

    Parameters
    ----------
    configuration
        Validated plasma-jet configuration.
    inputs
        Declared jet radius and launch radius.
    convergence_ratio
        Declared ``r_0 / r`` at stagnation; strictly greater than one.
    adiabatic_index
        ``gamma`` of the compressed volume; strictly greater than one.

    Returns
    -------
    Level0Physics
        The composed record.

    Raises
    ------
    DeviceConfigurationError
        If a declared input or a derived quantity falls outside its model
        bound; the refusals of the composed relations are raised
        unchanged, with the field they name.
    """
    ratio = require_convergence_ratio(convergence_ratio)
    array = array_state(configuration, inputs)
    return Level0Physics(
        configuration_digest_sha256=configuration.digest_sha256(),
        inputs=inputs,
        array=array,
        stagnation=stagnation_state(
            inputs.launch_radius_m,
            array.shell_mass_density_kg_m3,
            ratio,
            adiabatic_index,
        ),
    )
