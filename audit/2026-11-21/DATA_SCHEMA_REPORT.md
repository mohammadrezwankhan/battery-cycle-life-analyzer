# Data schema and validation audit

## Files and public ingestion contracts

- `load_cycle_data` in `bcla/datasets.py` reads CSV or TSV with configurable cycle/capacity columns and a normalize flag. `normalize=True` divides by first row's capacity; input must be a positive finite reference. Patch explicitly rejects negative cycle and capacity observations and non-finite normalized outputs. `normalize=False` only suppresses loader normalization; the downstream empirical fitter still expects normalized retention rather than raw Ah above its Q0 upper bound.
- `load_cycle_data_long_form` requires cell_id, cycle and capacity, normalizes per cell against earliest observed cycle when enabled, and preserves missing optional columns with `None`. Patch rejects negative capacity even without normalization. Numeric optional columns enforce finite values; depth of discharge must lie between 0 and 1; c_rate, rest_time_h, cycles_per_day and energy throughput are nonnegative.
- `load_duty_cycle_history` uses interval times and experiment_id with per-experiment envelopes. Missing fields do not become zero; empty/invalid fields have distinct parser paths.

## Per-cell envelopes

`_build_validation_envelope` groups by `cell_id` and emits cycle range and count, timestamp range/span, and per-cell min/max of temperature, C-rate, rest, usage frequency, DoD and energy throughput, using None bounds when absent. No imputed cycles or metadata are inserted. `_build_history_envelope` groups by (cell_id, experiment_id) and reports interval/duration and operating ranges.

## Safety boundaries and open questions

- Invalid physical data is rejected rather than projected as physically valid.
- Unseen operating conditions can trigger *out-of-envelope* interpretation only; recorded metadata are not covariates in the native model and cannot calibrate altered-duty predictions.
- Mixed timezone-aware and timezone-naive timestamp records within a cell or history experiment now raise an actionable ValueError before ordering or span calculations. Correct timezone offsets remain comparable using Python datetime arithmetic. Duplicate readings, mixed timezone conventions across *different* cells/experiments, and unusual encodings warrant further interoperability tests.
- EFC conventions: measured positive discharge current, clipped before interpolation, seconds to hours, nominal Ah denominator. External Oxford files were not incorporated into this branch.

## Evidence

New regressions: `tests/test_scientific_hardening.py`; existing: `tests/test_datasets.py`, `tests/test_dataset_domains.py`, `tests/test_equivalent_full_cycles.py`. See https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44944454660 .

## Second-pass verified corrections

`_require_comparable_timezones` checks awareness within each cell envelope, within each history interval, and across all history intervals for a cell/experiment. A mixed aware/naive sequence previously raised an uncontrolled TypeError; the new contract raises a labelled ValueError. `load_cycle_data_long_form(normalize=True)` now rejects non-finite outputs produced by dividing two individually finite capacities (fixture first 1e-6 Ah and later 1e308 Ah). Temporal validation now rejects negative future-only observations before computing holdout RMSE. All changes have red-then-green regression evidence in `tests/test_champion_scientific_review.py`.

The parser does not presume timezone-free values are UTC; it preserves naive values when an entire grouped series is naive. This is a consistency check, not an inferred timezone conversion.
