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

from .datasets import load_cycle_data  # re-exported convenience helper
