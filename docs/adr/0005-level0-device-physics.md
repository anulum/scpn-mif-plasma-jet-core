<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Plasma-Jet Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics: a jet array, and a spherical convergence

Status: accepted (2026-09-04). Adds the third implemented capability,
`level0_device_physics`, at `computational_prototype`, and pins the shared
kernel library for the first time in this repository.

## Context

The repository carried a configuration model and diagnostic semantics and
no physics. Its filed source, S. C. Hsu et al., arXiv:1201.1879 (2012), is
a study of whether 30 discrete plasma jets evolve toward a spherical
liner, and it prints the PLX array completely.

## Decision

1. **The relations are the ones the source's own question bears on.**

   *The array as a forming liner.* Its mass and kinetic energy are sums the
   configuration already computes. What is added is the fraction of the
   sphere the jets add up to — a jet of radius `r` launched from radius `R`
   subtends `arcsin(r/R)` and covers a cap of `2 pi (1 - cos theta)`, so
   `N` of them sum to `N (1 - cos theta) / 2` of the sphere — and the ram
   pressure `rho v^2` of the shell they are meant to form.

   *The convergence.* Density gain `(r_0/r)^3` and adiabatic temperature
   gain `(r_0/r)^(3(gamma-1))`.

2. **The exponent is three and that is the whole distinction.** The two
   other magneto-inertial families in this group implode a cylinder, where
   the gain is the area ratio and the exponent is two. This one implodes a
   sphere. The relations look like the cylindrical ones and are not them,
   which is why they are written here rather than borrowed, and why the
   dimension is a named constant rather than a literal three.

   At `gamma = 5/3` the spherical exponent is **exactly** `2.0` in binary
   — measured, not assumed — where the cylindrical `2 (gamma - 1)` is
   `1.3333333333333335` and is not exactly four thirds. The test asserts
   the equality here because it holds here.

3. **The coverage is a sum of cap areas, not a coverage map.** Caps cannot
   tile a sphere, so a fraction above one means the caps overlap somewhere
   and says nothing about whether any point is left bare. The docstring,
   the record's non-claims and the test all say so. **The merging of the
   jets is the subject of the filed source and is not modelled here.**

4. **Anchoring, and three printed numbers that check each other.**

   Printed: 30 jets, 50 km/s, a total liner mass of 300 mg, a total
   kinetic energy of 376 kJ, a jet radius of 5 cm, an initial mass density
   of 6.63e-4 kg/m^3 and a vacuum chamber 3 m across.

   The per-jet mass is not printed and follows exactly from two printed
   numbers: 300 mg over 30 jets is 10 mg, exact in binary.

   The energy checks the mass and the speed: half the printed total mass
   times the printed speed squared is 375.0 kJ against the printed 376 kJ,
   0.27 %. The anchor is asserted at half a per cent and says why — the
   source rounds its energy to three figures.

   And the printed density pins **the one value that had to be declared**.
   The source prints the chamber, not the sphere the jets are launched
   from. The radius at which the printed mass, spread over a shell one
   printed jet diameter thick, gives the printed density is 0.60 m —
   inside the printed chamber. That is what the fixture declares, and a
   test asserts the density comes back to better than a tenth of a per
   cent. It also checks that the shell idealisation this package uses
   matches the source's own.

## Consequences

The family has a physics capability bounded to two closed forms, anchored
on an array whose printed numbers check one another three ways.

Nothing here claims that the jets merge, that the liner is uniform, or
anything about a real machine.
