"""Regenerate the README/Pages preview from the documented synthetic NMC data."""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt

from bcla import core, datasets, viz


def main() -> None:
    cycles, capacity = datasets.synthetic_nmc(cycles=1000, seed=7)
    results = core.fit_all_models(cycles, capacity)
    figure = viz.model_comparison(results)
    output = Path(__file__).resolve().parents[1] / "docs/model_comparison_preview.png"
    try:
        figure.savefig(output, dpi=150, bbox_inches="tight")
    finally:
        plt.close(figure)
    sys.stdout.write(str(f"Preview written to {output}") + "\n")


if __name__ == "__main__":
    main()
