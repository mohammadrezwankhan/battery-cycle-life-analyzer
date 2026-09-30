# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

## [0.3.0] - Pending release

### Added

- Discharge equivalent-full-cycle integration for measured current time series,
  including partial-interval queries and strict input validation.
- An opt-in Oxford grid-battery real-data example with ODbL attribution,
  measured-profile canonicalization diagnostics, and bounded EOL reporting.

## [0.2.0] - 2026-08-26

### Added

- Chronological late-cycle holdout scoring and validation-based model selection.
- Residual-bootstrap EOL/RUL intervals with bounded-projection censoring and
  fit-failure reporting.
- Optional version-2 timestamped duty-cycle history with interval validation,
  operating-context preservation, and a synthetic example.

### Changed

- The multi-model CLI now uses validation-based selection by default; explicit
  in-sample RMSE selection remains available for compatibility and diagnostics.
- Temporal validation now keeps duplicate cycle indices together, rejects
  underidentified splits, and requires non-negative cycle indices.
- Bootstrap bounds are withheld after any censoring or fit failure and require
  residual degrees of freedom plus positive residual variance.

## [0.1.0] - 2026-07-25

### Added

- Linear, power-law, and logarithmic battery capacity-fade models.
- RMSE and R-squared diagnostics with lowest-RMSE model selection.
- Bounded end-of-life projection with an explicit unsupported-result path.
- Synthetic LFP and NMC demonstration datasets.
- CSV/TSV import for cycle-capacity data with normalization and validation.
- Provenance-aware long-form cycling data with validation-envelope metadata.
- Arrhenius temperature acceleration comparison.
- Publication-ready Matplotlib visualizations.
- Command-line interface and Colab demonstration notebook.
- Tests across Python 3.9, 3.10, 3.11, and 3.12.
- MIT license and contributor guidance.
