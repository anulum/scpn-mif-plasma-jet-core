<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Plasma Jet Core — ADR 0002: device configuration model
-->

# ADR 0002 — Device configuration model and evidence-maturity semantics

**Status:** accepted (2026-08-31)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The repository was established architecture-only (ADR 0001). The first
capability lane is the device configuration model for the single
registry configuration this repository owns (`plasma_jet_mif`). The
claim boundary and repository-level `evidence_maturity` semantics
follow the family pilot.

## Decision

1. The package `scpn_mif_plasma_jet_core` implements the device
   configuration model as frozen, strictly typed value objects: the
   plasma-gun jet array (jet count, per-jet mass and velocity).
2. Claim boundary — identical to the family pilot: internal-consistency
   validation, cited textbook estimates with documented bounds,
   canonical serialisation with SHA-256 digest, and the data-only SPO
   registry pin. No claim about any real machine; every exercised
   parameter set is a synthetic test fixture.
3. Hard invariant: at least two jets — a single jet cannot form the
   converging liner that defines plasma-jet magneto-inertial fusion.
4. Derived quantities from standard mechanics: per-jet and total
   kinetic energy ``E = n m v^2 / 2``. Advisory finding, reported by
   `consistency_report()` and never clamped: a jet count below ~30,
   under which a spherically convergent plasma liner is not formed in
   the documented gun-array designs (S. C. Hsu et al., IEEE Trans.
   Plasma Sci. 40 (2012) 1287).
5. Repository-level `evidence_maturity` = the highest state claimed by
   any capability entry; per-capability states are the authoritative
   claim surface.
6. Everything else is unchanged: review-only/non-actionable SPO
   profile, no adapter implementation, empty solver seams,
   `not_federated` Studio state, independent machine-protection veto,
   all non-claims.

## Consequences

- The Studio descriptor's `capabilities` array carries its first item
  (schema 1.1.0 data change only).
- The reactor-domain validator gains the populated-capabilities branch
  with the ceiling rule.
- Later lanes (launch/merging/compression diagnostic semantics with
  dual clocks, safety envelope) build on these types; maturity advances
  per capability only with the evidence the family standard requires.
