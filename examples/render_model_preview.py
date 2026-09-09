"""Regenerate the README/Pages preview from the documented synthetic NMC data."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from bcla import core, datasets, viz  # noqa: E402


def main() -> None:
    cycles, capacity = datasets.synthetic_nmc(cycles=1000, seed=7)
    results = core.fit_all_models(cycles, capacity)
    figure = viz.model_comparison(results)
    output = Path(__file__).resolve().parents[1] / "docs/model_comparison_preview.png"
    try:
        figure.savefig(output, dpi=150, bbox_inches="tight")
    finally:
        plt.close(figure)
    print(f"Preview written to {output}")


if __name__ == "__main__":
    main()
