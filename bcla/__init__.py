"""
bcla — Battery Cycle\u2011Life Analyzer
====================================

Fit degradation models to battery cycling data, project remaining
useful life, and generate publication\u2011ready figures.

Submodules
----------
core        \u2013 Data structures and model fitting
viz         \u2013 Plotting and figure exports
datasets    \u2013 Load example / built\u2011in cycling data and CSV helpers
"""

__version__ = "0.2.0"

from .datasets import (
    LongFormCycleData,
    equivalent_full_cycles,
    load_cycle_data,
    load_cycle_data_long_form,
    load_duty_cycle_history,
)  # re-exported convenience helpers

__all__ = [
    "LongFormCycleData",
    "equivalent_full_cycles",
    "load_cycle_data",
    "load_cycle_data_long_form",
    "load_duty_cycle_history",
]
