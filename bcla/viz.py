"""
viz — Publication‑quality plots for battery cycle‑life analysis.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from .core import FitResult, arrhenius_acceleration_factor

# ── Global style ────────────────────────────────────────────────────────

STYLE = {
    "figure.dpi":        150,
    "figure.facecolor":  "white",
    "axes.facecolor":    "white",
    "axes.edgecolor":    "0.3",
    "axes.grid":         True,
    "grid.alpha":        0.3,
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.labelsize":    12,
}


def _apply_style() -> None:
    for k, v in STYLE.items():
        plt.rcParams[k] = v


# ── Single plot helpers ─────────────────────────────────────────────────

def capacity_fade(result: FitResult,
                  ax: Optional[Axes] = None,
                  show_eol: bool = True,
                  eol_fraction: float = 0.8,
                  title: str = "Capacity Fade"
                  ) -> Axes:
    """
    Plot observed capacity vs. cycle with the fitted model, RMSE, and R².

    Parameters
    ----------
    result      : FitResult from ``bcla.core.fit_capacity_fade``.
    ax          : optional Matplotlib Axes.
    show_eol    : draw a horizontal EOL threshold line.
    eol_fraction : EOL definition (default 0.8 = 80 %).
    title       : plot title.

    Returns
    -------
    The Axes object.
    """
    _apply_style()
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4.5))

    ax.scatter(result.cycles, result.observed,
               s=18, c="#1f77b4", zorder=3, label="Observed")
    ax.plot(result.cycles, result.predicted,
            color="#d62728", linewidth=2, label=result.model_name)

    if show_eol:
        q0 = result.params["Q0"]
        ax.axhline(q0 * eol_fraction, color="grey", ls="--", lw=1,
                   label=f"EOL ({eol_fraction * 100:.0f} %)")

        eol_c = result.eol_cycle(eol_fraction)
        if eol_c is not None:
            ax.axvline(eol_c, color="grey", ls=":", lw=1, alpha=0.7)
            ax.annotate(f"EOL ≈ {eol_c:.0f}", xy=(eol_c, q0 * eol_fraction),
                        xytext=(eol_c * 0.6, q0 * (eol_fraction - 0.04)),
                        fontsize=10, color="grey",
                        arrowprops=dict(arrowstyle="->", color="grey"))

    # Metrics text box
    text = f"RMSE = {result.rmse:.5f}\nR²   = {result.r_squared:.4f}"
    ax.text(0.97, 0.05, text, transform=ax.transAxes,
            va="bottom", ha="right", fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.7))

    ax.set_xlabel("Cycle Number"); ax.set_ylabel("Normalised Capacity")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(bottom=max(0.65, result.observed.min() - 0.05))
    return ax


def model_comparison(results: dict[str, FitResult],
                     eol_fraction: float = 0.8
                     ) -> plt.Figure:
    """
    Side‑by‑side comparison of all fitted models on one figure.

    Parameters
    ----------
    results      : dict from ``bcla.core.fit_all_models``.
    eol_fraction : EOL threshold.

    Returns
    -------
    Matplotlib Figure (1 row × 3 columns).
    """
    _apply_style()
    names = list(results.keys())
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    for ax, name in zip(axes, names):
        capacity_fade(results[name], ax=ax, show_eol=True,
                      eol_fraction=eol_fraction, title=name.capitalize())
    fig.suptitle("Model Comparison — Capacity Fade", fontsize=14, y=1.04)
    fig.tight_layout()
    return fig


def eol_vs_temperature(q0: float,
                       k: float,
                       cycle_range: tuple[int, int] = (0, 3000),
                       temperatures: Optional[list[float]] = None,
                       eol_fraction: float = 0.8,
                       ax: Optional[Axes] = None
                       ) -> Axes:
    """
    Show how temperature accelerates EOL under a simple linear model.
    Uses the Arrhenius factor to scale the linear fade rate *k*.

    Parameters
    ----------
    q0           : initial normalised capacity.
    k            : linear fade rate at reference 25 °C.
    cycle_range  : (min, max) cycles to display.
    temperatures : list of temperatures °C to plot.
    ax           : optional Axes.
    eol_fraction : EOL definition.

    Returns
    -------
    Axes.
    """
    _apply_style()
    if temperatures is None:
        temperatures = [15, 25, 35, 45, 55]
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 4.5))

    cycles = np.linspace(*cycle_range, 2000)
    palette = plt.cm.plasma(np.linspace(0.2, 0.9, len(temperatures)))

    for temp, color in zip(temperatures, palette):
        af = arrhenius_acceleration_factor(temp)
        k_eff = k * af
        cap = q0 - k_eff * cycles
        label = f"{temp} °C (AF={af:.2f})"
        ax.plot(cycles, cap, color=color, lw=2, label=label)

    ax.axhline(q0 * eol_fraction, color="grey", ls="--", lw=1,
               label=f"EOL ({eol_fraction * 100:.0f} %)")
    ax.set_xlabel("Cycle Number"); ax.set_ylabel("Normalised Capacity")
    ax.set_title("Temperature Effect on Cycle Life (Arrhenius)")
    ax.legend(fontsize=8, loc="lower left")
    return ax
