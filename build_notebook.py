#!/usr/bin/env python
# ── Demo notebook export script ──────────────────────────────────────────
# Generates notebooks/demo.ipynb as a Jupyter notebook showcasing bcla.
import json
from pathlib import Path

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Battery Cycle‑Life Analyzer — Demo\n\n",
            "Select degradation models on late-cycle validation data, project remaining useful life, and visualise uncertainty.\n\n",
            "### Setup for a fresh Google Colab run\n",
            "If you open this notebook directly from GitHub in Colab, install bcla first:\n\n",
            "```bash\n",
            "python -m pip install --upgrade pip\n",
            "python -m pip install --quiet git+https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer.git\n",
            "```\n",
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "import importlib\n",
            "import subprocess\n",
            "import sys\n",
            "\n",
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "\n",
            "if 'google.colab' in sys.modules:\n",
            "    try:\n",
            "        import bcla  # type: ignore[import-not-found]\n",
            "    except ModuleNotFoundError:\n",
            "        subprocess.run([\"python\", \"-m\", \"pip\", \"install\", \"--quiet\", \"--upgrade\", \"pip\"], check=True)\n",
            "        subprocess.run([\"python\", \"-m\", \"pip\", \"install\", \"--quiet\", \"git+https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer.git\"], check=True)\n",
            "        importlib.invalidate_caches()\n",
            "        import bcla  # type: ignore[import-not-found]\n",
            "\n",
            "from bcla import core, datasets, viz"
        ],
        "outputs": []
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Use the reproducible NMC synthetic trajectory\n",
            "All synthetic data is fixed by default (seeded) for reproducible outputs."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "cycles, capacity = datasets.synthetic_nmc(cycles=1000, seed=7)\n",
            "print(f\"Cycles: {len(cycles)}, capacity range: [{capacity.min():.4f}, {capacity.max():.4f}]\")\n",
            "\n",
            "assert np.all(np.isfinite(cycles)) and np.all(np.isfinite(capacity))\n",
            "assert len(cycles) == len(capacity) > 0"
        ],
        "outputs": []
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Fit all degradation models\n",
            "This compares linear, power-law, and logarithmic models."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "results = core.fit_all_models(cycles, capacity)\n",
            "for name, r in results.items():\n",
            "    print(r.summary() + \"\\n\")"
        ],
        "outputs": []
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Temporal validation, EOL, and bootstrap interval\n",
            "Model selection uses the latest observations as a chronological holdout; the projection checks the bounded None case and reports EOL, RUL, and residual-bootstrap intervals."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "selection = core.select_model_by_validation(cycles, capacity)\n",
            "name, best = selection.model_name, selection.fit\n",
            "print(f\"Selected model: {name} (held-out RMSE = {selection.validation_score.rmse:.5f})\")\n",
            "eol = best.eol_cycle(eol_fraction=0.8)\n",
            "current_cycle = float(cycles[-1])\n",
            "if eol is None:\n",
            "    print(\"Projected EOL (80%): outside supported projection window\")\n",
            "    print(\"Projected RUL (80%): unavailable\")\n",
            "else:\n",
            "    rul_cycles = max(0.0, eol - current_cycle)\n",
            "    print(f\"Projected EOL (80%): {eol:.0f} cycles\")\n",
            "    print(f\"Projected RUL (80%): {rul_cycles:.0f} cycles\")\n",
            "\n",
            "interval = core.bootstrap_life_projection(best, samples=100, random_state=42)\n",
            "if interval.eol_lower is not None:\n",
            "    print(f\"95% EOL interval: {interval.eol_lower:.0f}–{interval.eol_upper:.0f} cycles\")\n",
            "    print(f\"95% RUL interval: {interval.rul_lower:.0f}–{interval.rul_upper:.0f} cycles\")\n",
            "else:\n",
            "    print(\n",
            "        \"Interval unavailable: \"\n",
            "        f\"successful={interval.successful_samples}, \"\n",
            "        f\"censored={interval.censored_samples}, \"\n",
            "        f\"failed={interval.failed_samples}, \"\n",
            "        f\"requested={interval.requested_samples}\"\n",
            "    )"
        ],
        "outputs": []
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## 4. Visualise fitted curves"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "fig = viz.model_comparison(results)\n",
            "fig.savefig(\"model_comparison.png\", dpi=150, bbox_inches=\"tight\")\n",
            "plt.show()"
        ],
        "outputs": []
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## 5. Temperature effect on cycle life"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "fig2, ax = plt.subplots(figsize=(8, 4.5))\n",
            "viz.eol_vs_temperature(q0=1.0, k=0.00018, temperatures=[15, 25, 35, 45, 55], ax=ax)\n",
            "fig2.savefig(\"temperature_effect.png\", dpi=150, bbox_inches=\"tight\")\n",
            "plt.show()"
        ],
        "outputs": []
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 6. Compare selected chemistry models\n",
            "Both are synthetic, illustrative trajectories (not validated chemistry benchmarks)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "x_lfp, y_lfp = datasets.synthetic_lfp(cycles=1500, seed=42)\n",
            "x_nmc, y_nmc = datasets.synthetic_nmc(cycles=1000, seed=7)\n",
            "\n",
            "chemistry_data = [(\"LFP\", x_lfp, y_lfp), (\"NMC\", x_nmc, y_nmc)]\n",
            "\n",
            "fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)\n",
            "for axis, (name, x, y) in zip((ax1, ax2), chemistry_data):\n",
            "    selected = core.select_model_by_validation(x, y)\n",
            "    best_name, best_result = selected.model_name, selected.fit\n",
            "    print(f\"{name} selected model: {best_name} (held-out RMSE={selected.validation_score.rmse:.5f})\")\n",
            "    viz.capacity_fade(best_result, ax=axis, title=f\"{name}: selected = {best_name}\")\n",
            "\n",
            "    eol = best_result.eol_cycle(eol_fraction=0.8)\n",
            "    if eol is not None:\n",
            "        print(f\"{name} projected 80% EOL (selected model): {eol:.0f} cycles\")\n",
            "    else:\n",
            "        print(f\"{name} 80% EOL (selected model): outside projection window\")\n",
            "\n",
            "fig3.suptitle(\"Chemistry Comparison\", fontsize=14, y=1.03)\n",
            "fig3.tight_layout()\n",
            "fig3.savefig(\"chemistry_comparison.png\", dpi=150, bbox_inches=\"tight\")\n",
            "plt.show()"
        ],
        "outputs": []
    }
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.0"}
    },
    "cells": cells
}

notebook_path = Path(__file__).resolve().parent / "notebooks" / "demo.ipynb"
notebook_path.parent.mkdir(parents=True, exist_ok=True)
with notebook_path.open("w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)
print(f"Demo notebook written to {notebook_path}.")
