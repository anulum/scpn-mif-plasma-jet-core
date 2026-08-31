<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Plasma Jet Core — Architecture summary
-->

# Architecture summary

`SCPN-MIF-PLASMA-JET-CORE` is the device-family owner for plasma-jet
magneto-inertial fusion systems inside the SCPN Reactor Systems Research
Group. The repository holds two implemented capabilities at
`computational_prototype` — the device configuration model (ADR 0002)
and the diagnostic and clock semantics model (ADR 0003), both in
`src/scpn_mif_plasma_jet_core/` — alongside the device boundary, its
ecosystem contracts, and the validation tooling that enforces both.

The authoritative architecture record is
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The ownership decision and
its consequences are fixed in
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).

Boundary in one paragraph: this repository owns plasma-jet-MIF plant and
experiment truth — configuration policy for gun arrays launching
high-Mach-number jets that merge into an imploding plasma liner
compressing a magnetised target, with timing-symmetry and
merging-uniformity budgets as the defining constraints, pulsed lifecycle
semantics with misfire and asymmetry hazard records, chamber-centred
diagnostic and clock declarations, actuator-response boundaries limited to
shot-to-shot array programming, safety-envelope declarations, and the
device-owned CONTROL adapter specification. Target physics belongs to its
owners (`SCPN-FRC-CORE`, `SCPN-MIF-CORE`); solver mathematics stays in
`SCPN-FUSION-CORE`; typed semantics stay in `SCPN-PHASE-ORCHESTRATOR`
(review-only); admitted control actions are formed only by `SCPN-CONTROL`;
independent machine protection keeps the final veto; portfolio
presentation belongs to `SCPN-STUDIO`, towards which this project is
`not_federated`.
