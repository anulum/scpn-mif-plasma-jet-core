<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Plasma Jet Core — Benchmarks and computation contract
-->

# Benchmarks and computation contract

## Computation contract

The level-0 physics of this package is a set of closed forms evaluated in
IEEE-754 binary64 on the Python floor (SI units internally; the
configuration carries the jet mass in milligrams and the jet speed in
kilometres per second):

| Module | Kernels | Operations |
|---|---|---|
| `physics/array.py` | jet and array mass and kinetic energy, jet half-angle `arcsin(r_jet / R)`, spherical coverage `N (1 - cos theta) / 2`, ram pressure `rho v^2`, the launch-shell density | `* /`, the constant `pi`, a square through the platform `pow`, the platform `asin` and `cos` |
| `physics/convergence.py` | spherical density gain `(r_0 / r)^3`, adiabatic temperature gain `(r_0 / r)^(3 (gamma - 1))` | `* /`, **one real power** |
| `physics/level0.py` | the composed record with canonical bytes and SHA-256 digest | composition, JSON serialisation |

Every input outside its domain is refused with the package error, never
clamped. The real power is not the platform `pow`: it is evaluated by the
shared library's deterministic `power` kernel (`numerics_transcendental`,
pinned in `reactor-domain.json`). The half-angle and coverage use the
platform `asin` and `cos`, which IEEE-754 does not require to be correctly
rounded, so a native backend that must agree bit for bit would need one
deterministic implementation of those on both sides. There are no physical
constants with an edition; the unit factors are bound by tests.

**Backend status.** Python floor only. There is no native crate. The
ecosystem production standard asks for a native path on required numeric
paths and allows a scoped, owner-approved exception for trivial non-hot
arithmetic; that decision is the owner's and is recorded as open in the
backlog. The benchmark marks the native backend as unavailable instead
of omitting it.

## Level-0 physics — local workstation (non-isolated)

Artefact: `benchmarks/results/level0_physics.local.json` (schema
`scpn-mif-plasma-jet-core.level0-physics-benchmark.v1`, generated
2026-10-31T09:59:07.919581+00:00, at commit `70661cb970c6` with the working
tree of the landing commit). Host: 11th Gen Intel(R) Core(TM) i5-11600K @
3.90GHz, Linux-7.0.0-34-generic-x86_64-with-glibc2.39, Python 3.12.3; load
average at start 10.86; cores not isolated, so treat the numbers as a smoke
timing, not a performance measurement. Parameters: 20000 closed-form points
and 2000 records, 3 warm-up passes, 20 timed passes.

### `closed_forms` (half-angle, coverage, ram pressure, density and temperature gains per point)

| Backend | P50 µs/point | P95 µs/point | P99 µs/point | mean µs/point | throughput points/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 3.295 | 3.870 | 4.395 | 3.224 | 303506 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

### `level0_record` (composed record with canonical bytes per point)

| Backend | P50 µs/record | P95 µs/record | P99 µs/record | mean µs/record | throughput records/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 66.734 | 92.192 | 96.254 | 64.520 | 14985 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

## Regenerate

```bash
.venv/bin/python benchmarks/level0_physics.py --label local
```

The script writes `benchmarks/results/level0_physics.<label>.json` with the
provenance above. A number from a fixed CI runner or isolated cores would
replace the smoke timing here; none is claimed yet.
