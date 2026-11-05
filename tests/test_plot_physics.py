"""Plot traces preserve the model's physical temperature and EOL behavior."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from bcla import core, viz


def test_temperature_plot_defaults_and_supplied_axes_preserve_arrhenius_slopes() -> None:
    defaults = viz.eol_vs_temperature(1.0, 0.0002)
    figure, axes = plt.subplots()
    try:
        result = viz.eol_vs_temperature(1.0, 0.0002, temperatures=[25.0, 50.0], ax=axes)
        assert result is axes
        assert len(defaults.lines) == 6
        reference, hot = axes.lines[:2]
        x = np.asarray(reference.get_xdata(), dtype=float)
        assert np.allclose(reference.get_ydata(), 1.0 - 0.0002 * x)
        assert np.all(np.asarray(hot.get_ydata())[1:] < np.asarray(reference.get_ydata())[1:])
        assert len(axes.lines) == 3
    finally:
        default_figure = defaults.figure
        assert isinstance(default_figure, Figure)
        plt.close(default_figure)
        plt.close(figure)


def test_capacity_plot_without_eol_and_with_censored_projection() -> None:
    x = np.arange(10, dtype=float) * 100.0
    fitted = core.fit_capacity_fade(x, 1.0 - 0.000001 * x, model="linear")
    assert fitted.eol_cycle() is None
    without = viz.capacity_fade(fitted, show_eol=False)
    censored = viz.capacity_fade(fitted, show_eol=True)
    try:
        assert len(without.lines) == 1
        assert len(censored.lines) == 2
        assert not any(text.get_text().startswith("EOL") for text in censored.texts)
    finally:
        without_figure, censored_figure = without.figure, censored.figure
        assert isinstance(without_figure, Figure)
        assert isinstance(censored_figure, Figure)
        plt.close(without_figure)
        plt.close(censored_figure)
