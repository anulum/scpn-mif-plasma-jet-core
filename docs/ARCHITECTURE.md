<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Plasma Jet Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-MIF-PLASMA-JET-CORE` is the device-family owner for plasma-jet
magneto-inertial fusion systems in the SCPN Reactor Systems Research Group
portfolio. The
repository owns one implemented capability — the device configuration model
at `computational_prototype` (`src/scpn_mif_plasma_jet_core/`, design record ADR 0002,
evidence record `VALIDATION.md#device-configuration-model`). Every other
section below describes boundaries and contracts. The claim inventory is
empty; capability and claim inventories are generated and drift-checked.

## The five-surface boundary

1. **Governing confinement physics** — the `plasma_jet_mif` configuration
   (converging plasma-jet liner, `magneto_inertial` registry family): an
   array of plasma guns launches high-Mach-number jets that merge in
   flight into a quasi-spherical imploding plasma liner, which compresses
   a magnetised target plasma at the chamber centre. The defining budgets
   are jet timing and momentum symmetry, merging uniformity (avoiding
   shock-seeded non-uniformity), and liner-on-target coupling. The liner
   is itself a plasma launched from standoff distance — distinguishing
   the scheme from the solid conducting liner of MagLIF and the slow
   mechanical/liquid liners; the magnetised target's own physics belongs
   to its owner (for an FRC target, `SCPN-FRC-CORE`).
2. **Primary driver and energy delivery** — the plasma-gun array
   (capacitor-driven coaxial guns with declared jet mass, velocity, and
   Mach number), gun-array geometry, and target-plasma formation systems
   as configuration facets.
3. **Plant and shot lifecycle** — single-shot lifecycle: target-plasma
   formation, gun-array charge, synchronised jet launch, jet merging and
   liner formation, liner implosion onto the target, stagnation and burn
   window, and disassembly. Device-level hazard semantics cover gun
   misfire, timing asymmetry, and incomplete merging.
4. **Diagnostic, reference-frame, and clock model** — chamber-centred
   coordinates with per-gun labels, jet velocimetry and imaging, liner
   uniformity imaging, target-compression and burn diagnostics, and
   microsecond-flight/nanosecond-stagnation clock identities declared
   separately.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE`, review-only semantics towards
   `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-MIF-PLASMA-JET-CORE (device truth: jet-array/merging policy, pulsed
                          lifecycle, symmetry diagnostics, safety
                          envelope, adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated, truthfully empty inventory |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `tools/` |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; unknown
  schemas are rejected by consumers.
- The Studio descriptor is derived deterministically and embeds the
  manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at `0.1.0-spec`.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate,
ratification of an SPO `ControlIntent`-class contract, or Studio federation
after a real capability passes producer and consumer gates — each recorded
as a versioned contract change in a new ADR.
