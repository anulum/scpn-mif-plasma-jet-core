# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma Jet Core — level-0 physics benchmark

"""Benchmark the level-0 physics of this package on the Python floor.

Follows the ecosystem benchmark standard: warm-up, repeated samples,
percentiles, one row per (operation, backend), unavailable backends marked
explicitly, full provenance in the artefact. Two operations are timed:

- ``closed_forms``: the jet half-angle, the spherical coverage fraction,
  the ram pressure, the spherical density gain and the adiabatic
  temperature gain over a deterministic grid of synthetic jet speeds and
  convergence ratios; each sample times one full grid pass;
- ``level0_record``: the composed level-0 record with its canonical bytes
  on the synthetic reference array inputs over a grid of jet speeds and
  convergence ratios; each sample times one full grid pass.

This package has no native crate. The ``rust_native`` row records that
explicitly instead of omitting it. Nothing measured here is a physics
claim, and a run on a loaded host is a smoke timing, not a performance
measurement.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import platform
import shutil
import statistics
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

ROOT: Final = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scpn_mif_plasma_jet_core.configuration import (  # noqa: E402
    DeviceConfiguration,
    RegistryBinding,
)
from scpn_mif_plasma_jet_core.parameters import JetArray  # noqa: E402
from scpn_mif_plasma_jet_core.physics import (  # noqa: E402
    ArrayInputs,
    adiabatic_temperature_gain,
    jet_half_angle_rad,
    level0_physics,
    ram_pressure_pa,
    solid_angle_coverage,
    spherical_density_gain,
)

SCHEMA: Final = "scpn-mif-plasma-jet-core.level0-physics-benchmark.v1"
NATIVE_STATUS: Final = (
    "unavailable: this package has no native crate; the level-0 kernels use "
    "+ - * /, the constant pi, the platform asin and cos, and one real "
    "power evaluated by the shared library's deterministic power kernel, "
    "and the decision on a native backend is open with the project owner"
)


def grid(points: int) -> list[tuple[float, float]]:
    """Build a deterministic synthetic grid of jet speeds and convergence ratios.

    Parameters
    ----------
    points
        Number of grid points.

    Returns
    -------
    list of (float, float)
        ``(jet_velocity_km_s, convergence_ratio)`` pairs, the speed between
        20 and 100 km/s and the convergence ratio between 2 and 30.
    """
    return [
        (20.0 + 80.0 * (index % 97) / 96.0, 2.0 + 28.0 * (index % 89) / 88.0)
        for index in range(points)
    ]


def configuration(jet_velocity_km_s: float) -> DeviceConfiguration:
    """Return a synthetic plasma-jet configuration; it describes nothing.

    Parameters
    ----------
    jet_velocity_km_s
        Speed of every jet.

    Returns
    -------
    DeviceConfiguration
        A ``plasma_jet_mif`` configuration with the round reference array.
    """
    return DeviceConfiguration(
        identifier="plasma_jet_mif",
        jets=JetArray(
            jet_count=12, jet_mass_mg=8.0, jet_velocity_km_s=jet_velocity_km_s
        ),
        registry=RegistryBinding(version="1.0.0", digest_sha256="0" * 64),
    )


def closed_forms_pass(sample_grid: list[tuple[float, float]]) -> float:
    """Evaluate the closed forms once over the grid.

    Parameters
    ----------
    sample_grid
        Jet-speed and convergence-ratio pairs.

    Returns
    -------
    float
        Checksum of the results, so the work cannot be optimised away.
    """
    total = 0.0
    for speed, ratio in sample_grid:
        total += jet_half_angle_rad(0.04, 0.8)
        total += solid_angle_coverage(12, 0.04, 0.8)
        total += ram_pressure_pa(1.0e-3, speed * 1.0e3)
        total += spherical_density_gain(ratio)
        total += adiabatic_temperature_gain(ratio)
    return total


def record_pass_factory() -> Callable[[list[tuple[float, float]]], float]:
    """Return a grid pass that composes and serialises level-0 records.

    Returns
    -------
    callable
        The pass; each grid point sets the jet speed and the convergence
        ratio of one record on the synthetic reference array inputs.
    """
    inputs = ArrayInputs(jet_radius_m=0.04, launch_radius_m=0.8)

    def record_pass(sample_grid: list[tuple[float, float]]) -> float:
        total = 0
        for speed, ratio in sample_grid:
            record = level0_physics(configuration(speed), inputs, ratio)
            total += len(record.canonical_bytes())
        return float(total)

    return record_pass


def measure(
    run: Callable[[list[tuple[float, float]]], float],
    sample_grid: list[tuple[float, float]],
    warmup: int,
    repeats: int,
) -> dict[str, float]:
    """Time repeated grid passes and summarise them.

    Parameters
    ----------
    run
        Grid pass to time.
    sample_grid
        Parameter grid.
    warmup
        Discarded leading passes.
    repeats
        Timed passes.

    Returns
    -------
    dict[str, float]
        Percentiles, mean, min, max in microseconds per grid point and the
        throughput in points per second (P50-based).
    """
    for _ in range(warmup):
        run(sample_grid)
    samples: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        run(sample_grid)
        samples.append((time.perf_counter_ns() - start) / 1e3 / len(sample_grid))
    ordered = sorted(samples)

    def percentile(fraction: float) -> float:
        return ordered[min(len(ordered) - 1, round(fraction * (len(ordered) - 1)))]

    p50 = percentile(0.5)
    return {
        "p50_us_per_point": p50,
        "p95_us_per_point": percentile(0.95),
        "p99_us_per_point": percentile(0.99),
        "mean_us_per_point": statistics.fmean(samples),
        "min_us_per_point": ordered[0],
        "max_us_per_point": ordered[-1],
        "throughput_points_per_s": 1e6 / p50,
    }


def provenance() -> dict[str, Any]:
    """Collect the environment provenance of a run.

    Returns
    -------
    dict[str, Any]
        Interpreter, platform, CPU model, commit and host-load context.
    """
    cpu_model = "unknown"
    with contextlib.suppress(OSError):
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                cpu_model = line.split(":", 1)[1].strip()
                break
    load = "unavailable"
    with contextlib.suppress(OSError):
        load = Path("/proc/loadavg").read_text(encoding="utf-8").split()[0]
    commit = "unknown"
    git = shutil.which("git")
    if git is not None:
        with contextlib.suppress(OSError):
            # A fixed argument vector with the resolved executable; no shell.
            commit = subprocess.run(  # noqa: S603
                [git, "rev-parse", "HEAD"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip()
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_model": cpu_model,
        "load_average_1min_at_start": load,
        "commit": commit,
        "isolated_cores": False,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark command-line interface.

    Parameters
    ----------
    argv
        Argument vector; None reads sys.argv.

    Returns
    -------
    int
        0 on completion.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--points", type=int, default=20_000)
    parser.add_argument("--record-points", type=int, default=2_000)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--label", default="local")
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "results")
    args = parser.parse_args(argv)
    sample_grid = grid(args.points)
    record_grid = grid(args.record_points)
    record_pass = record_pass_factory()
    results: list[dict[str, Any]] = [
        {
            "name": "closed_forms",
            "backend": "python_floor",
            "stats": measure(closed_forms_pass, sample_grid, args.warmup, args.repeats),
            "status": "measured",
        },
        {
            "name": "closed_forms",
            "backend": "rust_native",
            "stats": None,
            "status": NATIVE_STATUS,
        },
        {
            "name": "level0_record",
            "backend": "python_floor",
            "stats": measure(record_pass, record_grid, args.warmup, args.repeats),
            "status": "measured",
        },
        {
            "name": "level0_record",
            "backend": "rust_native",
            "stats": None,
            "status": NATIVE_STATUS,
        },
    ]
    artefact = {
        "schema": SCHEMA,
        "generated_at": datetime.now(UTC).isoformat(),
        "label": args.label,
        "platform": provenance(),
        "parameters": {
            "points": args.points,
            "record_points": args.record_points,
            "warmup": args.warmup,
            "repeats": args.repeats,
        },
        "results": results,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / f"level0_physics.{args.label}.json"
    target.write_text(
        json.dumps(artefact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"benchmark: wrote {target}")
    for row in results:
        print(f"  {row['name']} {row['backend']}: {row['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
