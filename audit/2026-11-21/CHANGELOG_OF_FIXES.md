# Audited implementation change log

| Path | Reason | Regression evidence |
| --- | --- | --- |
| `bcla/core.py` | Replace fixed-grid EOL approximation with a continuous bracketed root; keep 3× cap and right-censoring | Linear analytical exactness, out-of-cap censor, power/log references |
| `bcla/core.py` | Use log1p for near-zero logarithm; reject incompatible raw Ah and invalid Q0 guess | Small argument and raw Ah tests |
| `bcla/core.py` | Enforce positive independent cycle support, nonnegative observations, finite parameters, covariance and diagnostics | Distinct-coordinate, adversarial solver tests |
| `bcla/core.py` | Reject silent flattening in temporal validation; require nonnegative Arrhenius Ea | 2D input, late-knee and Ea tests |
| `bcla/datasets.py` | Reject negative cycle/capacity and non-finite normalization; enforce long-form physical capacity | CSV/TSV and long-form invalid input tests |
| `bcla/__main__.py` | Convert input/fit errors to actionable argparse failures; avoid overwriting input and atomically replace PNG | Missing data and output-collision tests |
| `bcla/__init__.py` | Match runtime version to installed package metadata (0.3.0), without re-release | Distribution parity regression |
| `CHANGELOG.md` | Clarify historical 0.3.0 publication note; record unreleased hardening work | Release governance report |
| `tests/test_scientific_hardening.py` | Deliberately red-then-green offline regression suite | GitHub Actions 44944259925 and 44944454660; final head verification outstanding |
| `audit/2026-11-21/*` | Publish evidence, risk register, gate decisions and limitations | This audit snapshot |

Compatibility: supported normalized 1D observations and public result structures remain available; invalid inputs that previously slipped through or failed cryptically now raise explicit errors. Numerical EOL estimates become continuous, so results may differ by less than an old grid spacing. The default CSV and PNG names remain unchanged. No new runtime dependencies except using already-installed SciPy's brentq. Deferred: covariance conditioning research, alternative heteroscedastic bootstrap, actual Oxford dataset reproducibility, cross-browser/screen-reader audit, independent reviewer sign-offs, final hardened CI if queued.

## Quality-gate repair evidence

The initial integrated hardening run 44944454664 was not accepted as green: Ruff failed and numerical line/branch coverage fell below its required 95% threshold. Additional reference and guard tests in commit 0c79e9a8… corrected the coverage shortfall without modifying its threshold. The subsequent hardening run 44945020410 passed the Python coverage job but identified five precise Ruff lint errors. Replacing `os.replace` with `Path.replace` and renaming unused mock arguments resolves the reported lint rule violations in source; final CI run is required to prove remediation.

## Second-pass source fixes (red phase 44958435880)

- `bcla/datasets.py`: consistent timestamp-awareness guards for long-form per-cell and duty-cycle history intervals; explicit finite-value check after long-form normalization.
- `bcla/core.py`: reject negative held-out capacity before scoring, expose `FitResult.active_bounds` with ASCII-safe summary warnings, reject malformed manually constructed negative-rate EOL projections.
- `tests/test_champion_scientific_review.py`: nine adversarial examples, including eight baseline-failing regressions and additional lower-bound ASCII output check.
- `CHANGELOG.md`, `audit/2026-11-21/*`: transparent provenance, current tests, and residual release blockers. No security, coverage or branch-protection gate was disabled.

A final Ruff N802 spelling correction is committed with this update. The source before that cosmetic correction passed the full 216-test standard matrix and Python-coverage quality gate but failed Ruff; CI on the new commit is mandatory.
