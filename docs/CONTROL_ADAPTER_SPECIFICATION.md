<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN MIF Plasma Jet Core — CONTROL adapter specification
-->

# CONTROL adapter specification

**Adapter identifier:** `scpn-mif-plasma-jet-core.control-adapter`  
**Contract version:** `0.1.0-spec` (specification only — **no implementation
exists**)  
**Consumer:** `SCPN-CONTROL` plugin protocol

This document is the device-owned contract through which a future
plasma-jet-MIF adapter would supply device truth to the SCPN control plane.
Publishing this specification creates no capability and no claim: an
implementation may appear only with the replay fixtures and evidence the
reactor family standard requires for `control_research_ready`, and it
enters CONTROL only through CONTROL's installed public contract with
real-surface tests.

## Authority model (non-negotiable semantics)

1. The adapter **supplies declarations and observations; it never
   actuates**. It exposes no verb that writes to plant hardware.
2. `SCPN-CONTROL` alone admits observations and forms `ControlAction`
   values. The adapter cannot construct, forward, or replay a
   `ControlAction`.
3. SPO semantic output consumed alongside adapter data is `review_only`
   (`actionable = false`); the adapter must not re-label it.
4. Independent machine protection retains the final veto on every plant
   path. The adapter declares the safety envelope; it does not implement
   protection.
5. Every adapter payload carries provenance (source, clock identity,
   contract version); CONTROL rejects payloads without it.

## Contract surfaces

### 1. Observation schema (device → CONTROL)

Declared per diagnostic channel:

- channel identifier and physical quantity with SI unit — including
  per-gun launch channels (charge voltage, jet velocity and mass
  proxies), jet-merging and liner-uniformity imaging, target-compression
  channels, and burn channels (yield, stagnation timing anchor) with
  exact definitions;
- coordinate convention (chamber-centred frame with per-gun labels) and
  spatial layout (scalar, per-gun array, or image-derived);
- sampling clock identity and timestamp semantics (microsecond-class
  flight and nanosecond-class stagnation time bases declared
  separately);
- uncertainty representation (declared per channel; absent uncertainty is
  an explicit `unquantified` marker, never an implied zero);
- validity and quality flags with fail-closed semantics.

### 2. State schema (device → CONTROL)

- shot lifecycle phase (`target_formation`, `array_charge`,
  `jet_launch`, `merging`, `implosion`, `stagnation_burn`,
  `disassembly`, `terminated`) with monotonic transition semantics and
  device-truth event records for gun misfire, timing asymmetry, and
  incomplete merging;
- configuration identity: the `plasma_jet_mif` registry configuration,
  the gun-array geometry and target-class revision, and the configuration
  policy revision that produced the shot;
- device availability state for control research (simulation, replay, HIL;
  live plant states are out of scope for this contract version).

### 3. Actuator-capability declaration (device → CONTROL)

For each actuator class (per-gun charge and trigger programming with
array-level timing tables, target-plasma formation systems, gas and
propellant feeds):

- declared capability envelope (bounds, slew limits, latency class) as
  device truth for CONTROL's admission checks — control authority is
  shot-to-shot array programming; intra-shot feedback is outside the
  flight timescale;
- explicit marker `direct_actuation: false` — the declaration describes
  what the plant could accept from a certified path; it is not a command
  surface and the adapter provides no command transport.

### 4. Safety-envelope declaration (device → CONTROL and protection review)

- machine-readable operational envelope (per-gun energy and voltage
  bounds, array simultaneity requirements, chamber load and repetition
  limits with applicability domains);
- declared device-level hazard semantics for misfire, asymmetric
  implosion, and chamber debris;
- statement of the independent machine-protection boundary this envelope
  is subordinate to.

### 5. Replay fixtures contract (evidence)

An implementation must ship replay fixtures that exercise every schema
above through CONTROL's real admission path: nominal shots, asymmetric and
misfire sequences, boundary-of-envelope cases, invalid-payload rejections,
and clock-mismatch rejections. Fixtures are versioned with the adapter and
their digests recorded; HIL evidence is additionally required before
`control_research_ready` may be declared.

## Versioning rules

- `0.x` specification versions may change with a recorded revision note in
  this file and a manifest update in the same commit.
- From the first implemented `1.0.0`, changes follow semantic
  compatibility: breaking schema changes require a major version, a
  translation path or governed deprecation, and re-run producer/consumer
  evidence on both sides.
- The manifest (`reactor-domain.json` → `control_adapter`) always records
  the exact contract version; validator and drift checks keep the two
  files in agreement.
