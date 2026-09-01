# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Plasma Jet Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the spherically convergent jet array, the
array-size gate the configuration model checks, and the merge-to-liner
sequence. The jet counts drawn are the repository's own constants: the
hard minimum of two guns and the documented convergent array size. The
right-hand text panel states only facts backed by the repository
itself.

Outputs (written next to this script):

- ``repo_header.png`` — the convergent jet array assembling its liner
  around the target (used by ``README.md``).
- ``repo_header_array_gate.png`` — two, twelve and thirty jets against
  the array gate.
- ``repo_header_merge_sequence.png`` — launch, merge and implode.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

MIN_JET_COUNT = 2
SPHERICAL_ARRAY_MIN_JETS = 30

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configuration", "plasma_jet_mif · converging jet liner"),
    ("Hard Invariant", "multi-jet array · at least two guns"),
    ("Array Gate", "below 30 jets flagged (not convergent)"),
    ("Reference", "Hsu et al., IEEE TPS 40 (2012) 1287"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.75,
        "MIF PLASMA",
        color="white",
        fontsize=25,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.705,
        "JET CORE",
        color="white",
        fontsize=25,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.645,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.605, 0.605], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.545
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def _core_glow(
    ax: Any,
    centre_x: float,
    centre_z: float,
    core_radius: float,
    halo_radius: float,
    gain: float = 1.0,
) -> None:
    """Draw the glowing target at the array centre."""
    grid_x = np.linspace(centre_x - halo_radius, centre_x + halo_radius, 150)
    grid_z = np.linspace(centre_z - halo_radius, centre_z + halo_radius, 150)
    mesh_x, mesh_z = np.meshgrid(grid_x, grid_z)
    rho = np.sqrt((mesh_x - centre_x) ** 2 + (mesh_z - centre_z) ** 2) / core_radius
    ax.contourf(
        mesh_x,
        mesh_z,
        np.exp(-rho * 1.8) * gain,
        levels=28,
        cmap=_glow_cmap(),
        alpha=0.92,
    )


def _jet(
    ax: Any,
    centre_x: float,
    centre_z: float,
    angle: float,
    gun_radius: float,
    head_radius: float,
    alpha: float = 0.9,
) -> None:
    """Draw one plasma jet: gun muzzle, plume and leading head."""
    unit_x, unit_z = np.cos(angle), np.sin(angle)
    ax.plot(
        [centre_x + unit_x * gun_radius, centre_x + unit_x * (gun_radius - 0.16)],
        [centre_z + unit_z * gun_radius, centre_z + unit_z * (gun_radius - 0.16)],
        color=STEEL,
        lw=4.0,
        alpha=0.85,
        solid_capstyle="butt",
    )
    along = np.linspace(0, 1, 60)
    radius = gun_radius - (gun_radius - head_radius) * along
    plume_x = centre_x + unit_x * radius
    plume_z = centre_z + unit_z * radius
    ax.plot(plume_x, plume_z, color=CYAN, lw=2.6, alpha=alpha * 0.6)
    ax.plot(plume_x, plume_z, color="white", lw=0.8, alpha=alpha * 0.35)
    ax.plot(
        centre_x + unit_x * head_radius,
        centre_z + unit_z * head_radius,
        "o",
        color=CYAN,
        ms=3.4,
        alpha=alpha,
    )


def generate_jet_array() -> None:
    """Generate ``repo_header.png``: the convergent jet array."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(-2.9, 2.9)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")

    _core_glow(ax, 0.0, 0.0, 0.26, 0.9)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)
    ax.plot(
        0.24 * np.cos(theta),
        0.24 * np.sin(theta),
        color=CYAN,
        lw=1.6,
        alpha=0.95,
    )

    ax.plot(
        0.72 * np.cos(theta),
        0.72 * np.sin(theta),
        color=PROBE,
        lw=1.2,
        alpha=0.5,
        ls=(0, (4, 3)),
    )
    ax.text(
        0.0,
        0.86,
        "merged plasma liner",
        color=PROBE,
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    for index in range(SPHERICAL_ARRAY_MIN_JETS):
        angle = 2.0 * np.pi * index / SPHERICAL_ARRAY_MIN_JETS
        gun_radius = 1.0 / np.sqrt(
            (np.cos(angle) / 2.72) ** 2 + (np.sin(angle) / 1.32) ** 2
        )
        _jet(ax, 0.0, 0.0, angle, gun_radius, 0.80, alpha=0.85)

    ax.text(
        -2.62,
        1.24,
        f"{SPHERICAL_ARRAY_MIN_JETS} convergent guns",
        color=CYAN,
        fontsize=8.5,
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        2.35,
        -1.26,
        "standoff drive · no solid liner",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="right",
    )
    _text_panel(fig, "A Liner Made Of Jets")
    _save(fig, plt, "repo_header.png")


def generate_array_gate() -> None:
    """Generate ``repo_header_array_gate.png``: the array-size gate."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)

    panels = [
        (
            1.85,
            MIN_JET_COUNT,
            f"{MIN_JET_COUNT} jets",
            "hard minimum · accepted",
            RED,
            "not spherically convergent · FLAGGED",
        ),
        (
            5.0,
            12,
            "12 jets",
            "still below the array gate",
            RED,
            f"below {SPHERICAL_ARRAY_MIN_JETS} · FLAGGED",
        ),
        (
            8.15,
            SPHERICAL_ARRAY_MIN_JETS,
            f"{SPHERICAL_ARRAY_MIN_JETS} jets",
            "documented convergent array",
            GREEN,
            "Hsu et al., IEEE TPS 40 (2012) 1287",
        ),
    ]
    for centre_x, jets, title, subtitle, colour, note in panels:
        _core_glow(
            ax,
            centre_x,
            0.15,
            0.16,
            0.55,
            gain=0.5 + 0.5 * (jets / SPHERICAL_ARRAY_MIN_JETS),
        )
        ax.plot(
            centre_x + 0.14 * np.cos(theta),
            0.15 + 0.14 * np.sin(theta),
            color=CYAN,
            lw=1.3,
            alpha=0.95,
        )
        for index in range(jets):
            angle = 2.0 * np.pi * index / jets
            _jet(ax, centre_x, 0.15, angle, 1.32, 0.46, alpha=0.8)
        ax.text(
            centre_x,
            2.05,
            title,
            color="#99bbdd",
            fontsize=9,
            fontfamily="monospace",
            ha="center",
            alpha=0.95,
        )
        ax.text(
            min(centre_x, 7.95),
            1.72,
            subtitle,
            color=colour,
            fontsize=7.5,
            fontfamily="monospace",
            ha="center",
            alpha=0.95,
        )
        ax.text(
            centre_x,
            -2.15,
            note,
            color="#445566",
            fontsize=7.5,
            fontfamily="monospace",
            ha="center",
        )

    for divider_x in (3.42, 6.58):
        ax.plot(
            [divider_x, divider_x],
            [-1.8, 1.9],
            color=STEEL,
            lw=0.8,
            alpha=0.4,
        )
    ax.text(
        5.0,
        -2.85,
        "two guns pass the hard rule; only the documented array passes "
        "the convergence check",
        color=PROBE,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.85,
    )
    _text_panel(fig, "How Many Jets Make A Liner")
    _save(fig, plt, "repo_header_array_gate.png")


def generate_merge_sequence() -> None:
    """Generate ``repo_header_merge_sequence.png``: the assembly."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)

    stages = [
        (1.85, 1.05, 0.30, "launch", "guns fire discrete jets"),
        (5.0, 0.68, 0.60, "merge", "jets coalesce into a shell"),
        (8.15, 0.34, 1.0, "implode", "liner compresses the target"),
    ]
    for centre_x, head_radius, gain, title, subtitle in stages:
        _core_glow(ax, centre_x, 0.15, 0.14 + 0.10 * gain, 0.6, gain=gain)
        ax.plot(
            centre_x + 0.13 * np.cos(theta),
            0.15 + 0.13 * np.sin(theta),
            color=CYAN,
            lw=1.3,
            alpha=0.95,
        )
        for index in range(16):
            angle = 2.0 * np.pi * index / 16
            _jet(ax, centre_x, 0.15, angle, 1.28, head_radius, alpha=0.8)
        if title != "launch":
            ax.plot(
                centre_x + head_radius * np.cos(theta),
                0.15 + head_radius * np.sin(theta),
                color=PROBE,
                lw=1.3,
                alpha=0.75 if title == "merge" else 0.95,
                ls=(0, (4, 3)) if title == "merge" else "-",
            )
        ax.text(
            centre_x,
            -1.75,
            title,
            color="#99bbdd",
            fontsize=9,
            fontfamily="monospace",
            ha="center",
            alpha=0.95,
        )
        ax.text(
            centre_x,
            -2.1,
            subtitle,
            color="#445566",
            fontsize=7.5,
            fontfamily="monospace",
            ha="center",
        )

    ax.annotate(
        "",
        xy=(6.6, 2.5),
        xytext=(3.4, 2.5),
        arrowprops={"arrowstyle": "->", "color": STEEL, "lw": 1.2, "alpha": 0.7},
    )
    ax.text(
        5.0,
        2.72,
        "time",
        color="#667799",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        5.0,
        -2.8,
        "the liner is assembled in flight · declared, validated, never fired",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Launch, Merge, Implode")
    _save(fig, plt, "repo_header_merge_sequence.png")


if __name__ == "__main__":
    generate_jet_array()
    generate_array_gate()
    generate_merge_sequence()
