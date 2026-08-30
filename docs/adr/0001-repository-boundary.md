<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Plasma Jet Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. Plasma-jet MIF sits between the other
liner owners (MagLIF, mechanical/liquid) and the owners of its candidate
magnetised targets (FRC physics, the MIF merge-compression workflow); a
boundary decision was needed on all edges.

## Decision

1. `SCPN-MIF-PLASMA-JET-CORE` owns exactly one registry configuration:
   `plasma_jet_mif` (converging plasma-jet liner).
2. The repository owns device-level truth only: gun-array and jet-merging
   configuration policy (array geometry, jet mass/velocity/Mach
   declarations, timing-symmetry and merging-uniformity budgets), pulsed
   lifecycle semantics with misfire and asymmetry hazard records,
   symmetry/compression/burn diagnostic and clock declarations,
   actuator-response model boundaries, the safety-envelope declaration,
   and the device-owned CONTROL adapter specification.
3. The magnetised target's own physics belongs to its owner: FRC targets
   to `SCPN-FRC-CORE`, and the pulsed FRC merge-compression workflow with
   its trigger and RTL to `SCPN-MIF-CORE`. This repository owns the liner
   scheme, not the target.
4. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
5. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
6. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **One repository for all liner-MIF schemes**: rejected — a standoff
  plasma liner formed by merging jets, a solid conducting liner on
  nanosecond pulsed power, and slow mechanical/liquid liners differ in
  liner physics, driver, timescale, and hazards (surfaces 1–4).
- **Folding plasma-jet MIF into the FRC or MIF-CORE repositories**
  (candidate target overlap): rejected — the jet-liner scheme is a driver
  architecture independent of a particular target; owning it beside one
  target would blur the map's one-owner rule.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity for the plasma-jet-MIF
  configuration and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
