"""Rendered-layout checks for the documented synthetic NMC example."""

import matplotlib
import pytest

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402
from matplotlib.text import Annotation  # noqa: E402

from bcla import core, datasets, viz  # noqa: E402


@pytest.mark.parametrize("model", ["linear", "power_law", "logarithmic", "all"])
def test_eol_annotation_does_not_overlap_fit_metrics(model):
    cycles, capacity = datasets.synthetic_nmc(cycles=1000, seed=7)
    results = core.fit_all_models(cycles, capacity)
    if model == "all":
        figure = viz.model_comparison(results)
    else:
        figure = viz.capacity_fade(results[model]).figure

    try:
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        for axis in figure.axes:
            annotations = [
                text for text in axis.texts if isinstance(text, Annotation)
            ]
            metrics = [
                text for text in axis.texts if text.get_text().startswith("RMSE")
            ]
            assert len(annotations) == len(metrics) == 1
            # Include the arrow and the padded statistics box, not only text.
            annotation_box = annotations[0].get_window_extent(renderer)
            metrics_box = metrics[0].get_bbox_patch().get_window_extent(renderer)
            assert annotation_box.width > 1 and annotation_box.height > 1
            assert not annotation_box.overlaps(metrics_box), axis.get_title()
    finally:
        plt.close(figure)
