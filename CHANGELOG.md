# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Scientific hardening audit (2026-11-21; unreleased branch)

- Solve bounded EOL crossings with continuous root finding instead of discretized scan.
- Harden normalized-capacity fitting, finite solver results and covariance, distinct cycles, and chronological input shapes.
- Reject negative physical cycle/capacity observations in CSV and long-form loaders.
- Give actionable CLI errors for invalid inputs and write figures with atomic replacement.
- Correct the runtime __version__ attribute to match declared package version 0.3.0 without publishing a new release.
- Add adversarial regression coverage and audit evidence under audit/2026-11-21/.
- Second-pass hardening: reject incompatible timestamp awareness and non-finite long-form normalized values; block negative late holdout capacity; surface Q0/power-law beta fitted constraint warnings; reject manually constructed EOL results with invalid degradation parameters.
- Preserve cell-level duty-cycle history provenance when cell/experiment identifiers contain the delimiter: escape individual key components and verify distinct envelopes with an adversarial regression.
- Independently recheck four Oxford measured cells against their source archive without redistributing licensed measurements; leave two large BMR cells and cross-browser accessibility explicitly unverified.

## [0.3.0] - 2026-10-08 (published distribution; see release note)

The date is recorded in the maintainer release playbook as the PyPI 0.3.0 distribution upload; GitHub currently has a v0.3.0 tag but no matching published GitHub Release object. Editing this note does not re-tag, republish, or deploy anything.

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


## Documentation snapshot — 2026-11-19

This documentation-only package adds a canonical developer/scientific/maintainer/owner handbook, source/interface accounting, a reproducible static reading view, existing-site navigation and a proposed twelve-calendar-month roadmap. Native numerical code, workflows, dependencies, notebook/data/results, license and citation content are preserved.

This entry does not announce a software release or certify a deployment. Existing release headings above remain historical source text. The [release playbook](docs/maintainer/CI_CD_AND_RELEASE_PLAYBOOK.md) records the observed difference between package/runtime/changelog and published artifact identities.
