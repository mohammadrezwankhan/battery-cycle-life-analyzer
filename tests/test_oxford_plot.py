"""Regression checks for the Oxford example's measured-EFC figure."""

import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from bcla import core, viz  # noqa: E402
from examples import oxford_energy_trading as oxford  # noqa: E402


def test_oxford_figure_exposes_bounded_projection_on_measured_efc_axis():
    efc = np.linspace(0.0, 1500.0, 13)
    capacity = 1.0 - 0.00008 * efc
    results = core.fit_all_models(efc, capacity)
    figure = viz.model_comparison(results)

    try:
        oxford._decorate_efc_figure(figure, results, "BMR_cell1")

        assert figure._suptitle.get_text() == (
            "BMR cell 1: Model Comparison on Measured Discharge EFC"
        )
        assert [axis.get_title() for axis in figure.axes] == [
            "Linear",
            "Power Law",
            "Logarithmic",
        ]
        assert all(
            axis.get_xlabel() == "Measured Discharge EFC"
            for axis in figure.axes
        )
        assert all(
            any(line.get_label() == "Bounded projection" for line in axis.lines)
            for axis in figure.axes
        )
        threshold = min(result.params["Q0"] * 0.8 for result in results.values())
        assert figure.axes[0].get_ylim()[0] < threshold
    finally:
        plt.close(figure)
