"""
bcla — Battery Cycle‑Life Analyzer
====================================

Fit degradation models to battery cycling data, project remaining
useful life, and generate publication‑ready figures.

Submodules
----------
core        – Data structures and model fitting
viz         – Plotting and figure exports
datasets    – Load example / built‑in cycling data and CSV helpers
"""

__version__ = "0.1.0"

from .datasets import (
    LongFormCycleData,
    load_duty_cycle_history,
    load_cycle_data,
    load_cycle_data_long_form,
)  # re-exported convenience helpers
