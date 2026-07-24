#!/usr/bin/env python
# ── Demo notebook export script ──────────────────────────────────────────
# Generates notebooks/demo.ipynb as a Jupyter notebook showcasing bcla.
import json

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Battery Cycle‑Life Analyzer — Demo\n\n",
            "Fit degradation models, project remaining useful life, and visualise results.\n\n",
            "```\npip install -e .\n```"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "from bcla import core, viz, datasets"
        ],
        "outputs": []
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## 1. Load synthetic LFP cycling data"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "cycles, capacity = datasets.synthetic_lfp(cycles=1500, seed=42)\n",
            "print(f\"Cycles: {len(cycles)}, capacity range: [{capacity.min():.4f}, {capacity.max():.4f}]\")"
        ],
        "outputs": []
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## 2. Fit all degradation models"]
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
        "source": ["## 3. Best model & EOL projection"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "name, best = core.best_model(results, criterion=\"rmse\")\n",
            "print(f\"Best model: {name} (R² = {best.r_squared:.4f})\")\n",
            "eol = best.eol_cycle(eol_fraction=0.8)\n",
            "print(f\"Projected EOL (80%): {eol:.0f} cycles\" if eol else \"EOL not reached within range\")"
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
        "source": ["## 6. Compare LFP vs NMC chemistry"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [
            "x_lfp, y_lfp = datasets.synthetic_lfp(cycles=1200)\n",
            "x_nmc, y_nmc = datasets.synthetic_nmc(cycles=1200)\n",
            "\n",
            "fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)\n",
            "r_lfp = core.fit_capacity_fade(x_lfp, y_lfp, model=\"power_law\")\n",
            "r_nmc = core.fit_capacity_fade(x_nmc, y_nmc, model=\"linear\")\n",
            "viz.capacity_fade(r_lfp, ax=ax1, title=\"LFP (power‑law fit)\")\n",
            "viz.capacity_fade(r_nmc, ax=ax2, title=\"NMC (linear fit)\")\n",
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

import os
os.makedirs("/home/user/battery-cycle-life-analyzer/notebooks", exist_ok=True)
with open("/home/user/battery-cycle-life-analyzer/notebooks/demo.ipynb", "w") as f:
    json.dump(nb, f, indent=2)
print("Demo notebook written.")
