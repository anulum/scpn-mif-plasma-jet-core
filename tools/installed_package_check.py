# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma Jet Core — installed-wheel contract check

"""Exercise the installed package from outside the source checkout.

The installed-wheel workflow builds the wheel, installs it into a clean
environment and runs this script with ``python -I`` from a directory
outside the checkout. The script fails closed unless the package was
imported from the environment rather than the checkout, ships its
``py.typed`` marker, reports matching installed metadata with the pinned
kernel dependency, and serves the public path: a canonical configuration
document, a deterministic level-0 record of the anchor (which calls the
kernel library's power kernel), and the committed diagnostic-plan and
envelope fixture read through the installed parsers and verified against
each other. The fixture is read as data from the checkout; no checkout code
is imported.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import sys
from pathlib import Path
from typing import Final

DISTRIBUTION: Final = "scpn-mif-plasma-jet-core"
PACKAGE: Final = "scpn_mif_plasma_jet_core"
KERNEL_REQUIREMENT: Final = "scpn-reactor-kernels"
FIXTURE: Final = Path("tests") / "data" / "plan_envelope_fixture.json"

CONFIGURATION_DOCUMENT: Final = (
    b'{"identifier":"plasma_jet_mif","jets":{"jet_count":30,"jet_mass_mg":10.0,'
    b'"jet_velocity_km_s":50.0},"registry":{"digest_sha256":'
    b'"0000000000000000000000000000000000000000000000000000000000000000",'
    b'"version":"1.0.0"}}\n'
)
"""The anchor configuration of the test suite (Hsu et al., arXiv:1201.1879).

It serves only as a regression anchor for the installed package; nothing is
asserted about the array the paper describes.
"""

ARRAY_INPUTS: Final[dict[str, float]] = {"jet_radius_m": 0.05, "launch_radius_m": 0.6}
"""Declared array inputs of the anchor."""

CONVERGENCE_RATIO: Final = 10.0
"""Convergence ratio the level-0 tests evaluate at."""


def failed(checks: list[tuple[bool, str]]) -> list[str]:
    """Return the messages of the checks that did not hold.

    Parameters
    ----------
    checks
        Pairs of an outcome and the finding reported when it is false.

    Returns
    -------
    list[str]
        Findings in check order.
    """
    return [message for holds, message in checks if not holds]


def layout_findings(package_dir: Path, checkout: Path) -> list[str]:
    """Check where the package was imported from and what it ships.

    Parameters
    ----------
    package_dir
        Directory of the imported package.
    checkout
        Source checkout the installed package must not come from.

    Returns
    -------
    list[str]
        Findings; empty when the package lies outside the checkout and
        carries its ``py.typed`` marker.
    """
    return failed(
        [
            (
                not package_dir.resolve().is_relative_to(checkout.resolve()),
                f"{PACKAGE} imported from the checkout: {package_dir}",
            ),
            (
                (package_dir / "py.typed").is_file(),
                f"{PACKAGE} ships no py.typed marker",
            ),
        ]
    )


def metadata_findings(
    version: str,
    distribution_name: str = DISTRIBUTION,
    required: str = KERNEL_REQUIREMENT,
) -> list[str]:
    """Check the installed distribution metadata.

    Parameters
    ----------
    version
        ``__version__`` of the imported package.
    distribution_name
        Installed distribution to read.
    required
        Requirement the distribution must declare.

    Returns
    -------
    list[str]
        Findings; empty when the distribution is installed with the same
        version and declares the required dependency.
    """
    try:
        distribution = importlib.metadata.distribution(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        return [f"{distribution_name} is not installed"]
    requirements = distribution.requires or []
    return failed(
        [
            (
                distribution.version == version,
                f"installed version {distribution.version} != package {version}",
            ),
            (
                any(item.startswith(required) for item in requirements),
                f"{distribution_name} does not require {required}",
            ),
        ]
    )


def public_path_findings(checkout: Path) -> list[str]:
    """Serve the public path through the installed package.

    Parameters
    ----------
    checkout
        Checkout holding the committed plan and envelope fixture (data).

    Returns
    -------
    list[str]
        Findings; empty when the configuration round-trips byte for byte,
        the level-0 record is deterministic, and the fixture plan and
        envelope parse, verify and round-trip.
    """
    from scpn_mif_plasma_jet_core import (
        configuration_from_bytes,
        envelope_from_bytes,
        envelope_from_record,
        plan_from_bytes,
        plan_from_record,
        verify_envelope,
    )
    from scpn_mif_plasma_jet_core.physics import ArrayInputs, level0_physics

    configuration = configuration_from_bytes(CONFIGURATION_DOCUMENT)
    inputs = ArrayInputs(**ARRAY_INPUTS)
    record = level0_physics(configuration, inputs, CONVERGENCE_RATIO)
    document = json.loads((checkout / FIXTURE).read_bytes().decode("utf-8"))
    plan = plan_from_record(document["plan"])
    envelope = envelope_from_record(document["envelope"])
    verify_envelope(envelope, plan)
    return failed(
        [
            (
                configuration.canonical_bytes() == CONFIGURATION_DOCUMENT,
                "configuration did not round-trip byte for byte",
            ),
            (
                record.canonical_bytes()
                == level0_physics(
                    configuration, inputs, CONVERGENCE_RATIO
                ).canonical_bytes(),
                "level-0 record is not deterministic",
            ),
            (
                plan_from_bytes(plan.canonical_bytes()) == plan,
                "plan did not round-trip through its canonical bytes",
            ),
            (
                envelope_from_bytes(envelope.canonical_bytes()) == envelope,
                "envelope did not round-trip through its canonical bytes",
            ),
        ]
    )


def check_installed(checkout: Path) -> list[str]:
    """Run every installed-package check.

    Parameters
    ----------
    checkout
        Source checkout the package must not be imported from.

    Returns
    -------
    list[str]
        All findings; empty when the installed package meets its contract.
    """
    package = importlib.import_module(PACKAGE)
    package_dir = Path(package.__file__ or "").parent
    findings = layout_findings(package_dir, checkout)
    findings += metadata_findings(str(package.__version__))
    findings += public_path_findings(checkout)
    return findings


def report(findings: list[str]) -> int:
    """Print the outcome and return its exit status.

    Parameters
    ----------
    findings
        Findings of :func:`check_installed`.

    Returns
    -------
    int
        ``0`` without findings, else ``1``.
    """
    if findings:
        print("installed-package: FAIL", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1
    print("installed-package: PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the installed-package check from the command line.

    Parameters
    ----------
    argv
        Argument vector; ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` when the installed package meets its contract, else ``1``.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    args = parser.parse_args(argv)
    return report(check_installed(args.checkout))


if __name__ == "__main__":
    sys.exit(main())
