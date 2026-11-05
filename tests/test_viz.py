"""Rendered-layout checks for the documented synthetic NMC example."""

from __future__ import annotations

from typing import Callable, cast

import matplotlib
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg, RendererAgg
from matplotlib.figure import Figure, SubFigure

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.text import Annotation

from bcla import core, datasets, viz


@pytest.mark.parametrize("model", ["linear", "power_law", "logarithmic", "all"])
@pytest.mark.parametrize("cycle_count", [1000, 1500])
def test_eol_annotation_does_not_overlap_fit_metrics(model: str, cycle_count: int) -> None:
    cycles, capacity = datasets.synthetic_nmc(cycles=cycle_count, seed=7)
    results = core.fit_all_models(cycles, capacity)
    figure: Figure | SubFigure
    if model == "all":
        figure = viz.model_comparison(results)
    else:
        figure = viz.capacity_fade(results[model]).figure

    assert isinstance(figure, Figure)
    try:
        figure.canvas.draw()
        canvas = figure.canvas
        assert isinstance(canvas, FigureCanvasAgg)
        renderer = cast(Callable[[], RendererAgg], canvas.get_renderer)()
        for axis in figure.axes:
            annotations = [text for text in axis.texts if isinstance(text, Annotation)]
            metrics = [text for text in axis.texts if text.get_text().startswith("RMSE")]
            assert len(annotations) == len(metrics) == 1
            expected_alignment = "left" if cycle_count == 1000 else "right"
            assert metrics[0].get_horizontalalignment() == expected_alignment
            assert (annotations[0].xy[0] >= cycles[-1]) == (cycle_count == 1000)
            # Include the arrow and the padded statistics box, not only text.
            annotation_box = annotations[0].get_window_extent(renderer)
            metrics_patch = metrics[0].get_bbox_patch()
            assert metrics_patch is not None
            metrics_box = metrics_patch.get_window_extent(renderer)
            assert annotation_box.width > 1 and annotation_box.height > 1
            assert not annotation_box.overlaps(metrics_box), axis.get_title()
    finally:
        plt.close(figure)
