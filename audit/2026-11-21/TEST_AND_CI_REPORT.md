# Test and CI evidence register (2026-11-21)

## Baseline

- SHA `fe5bb6fca3345f8fa03a025a787bc2e3f9ca2c7d`; GitHub Actions https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44869544391 . Python 3.9/3.10/3.11/3.12 jobs succeeded. Py3.9: 190 passed, 6 skipped. Py3.12: 190 passed, 6 skipped, 13 subtests passed, 7.37 s test execution. Test command `python -m pytest -v` after `python -m pip install -e ".[dev]"`.
- All six skipped tests are `test_official_oxford_files_reproduce_audited_efc` variants BMP_cell1/2, BMR_cell1/2, SPM_cell1/2 in `tests/test_oxford_live.py`. That file runs only on BCLA_RUN_OXFORD_LIVE=1; it additionally skips when the external archive returns HTTP 403. No test skip is interpreted as measured-data success.

## Red-phase evidence

- Commit `c5e3b0f4c992104c8a597bc960b4c08de0ef2377` introduced 11 new tests before repairs. Run https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44944259925 : on Python 3.12, **10 failed, 191 passed, 6 skipped, 13 subtests passed**. Failures reproduced in same matrix. Ten failures involved EOL discretization, near-zero log cancellation, raw Ah diagnostics, 2D flatten, underidentified cycles, non-finite covariance/results, negative CSV inputs, and missing CSV CLI failure. One unchanged guard (beyond-cap EOL) passed.

## First corrected integrated candidate

- SHA `a19276ac57e03d869c74cab7f8631acf0cc8f4df`; https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44944454660 . Py3.9/3.10/3.11/3.12 all succeeded; Py3.12 summary: **201 passed, 6 skipped, 13 subtests passed in 7.44 s**.
- https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44944454661 successful candidate sdist/wheel build, `twine check --strict`, separate venv wheel install, `pip check`, import and CLI/PNG smoke outside checkout. Validated but not published.
- https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44944454689 CodeQL success.
- https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44944454664 Hardened CI awaiting completion at initial reporting; it includes SAST, secrets, dependencies, Trivy, and seven Python/browser quality modes. Do not mark passing before a run result.

## Final commit verification requirement

Subsequent metadata, extra regressions and report changes trigger a new PR head. **Do not reuse a previous green run to certify a later SHA**. Collect final `head_sha`, four Python matrix results, hardened CI results, package validation, CodeQL and skip details after pushing. The audit snapshot is not a claimed final green result for an unrun tree. Performance before/after timings above use distinct test inventories; they cannot support an optimization percentage.
