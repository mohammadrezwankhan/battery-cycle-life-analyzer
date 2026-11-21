# Scientific audit report

## Modelling contract

`Q(n) = Q0 - kn`, `Q(n) = Q0 - αn^β`, and `Q(n) = Q0 - a log(1+bn)` are empirical retention curves, not calibrated chemistry- or protocol-aware degradation laws. The admissible fitted `Q0` range is 0.5–1.5 normalized retention; power exponent β is bounded 0.1–2.0. The direct fitter cannot safely accept raw Ah above that range. A superlinear degradation *loss* need not imply convex retained capacity.

## Numerical solver

Source: `bcla/core.py`. Fixes enforce one-dimensional finite nonnegative capacity observations, distinct cycle coordinates exceeding model parameter count, clear failure on raw Ah outside the normalized fit envelope, explicit valid starting Q0, and rejection of non-finite fitted parameters, covariance and diagnostics. Solver convergence is not proof of reliable parameter identifiability; finite covariance need not imply a well-conditioned inverse problem. `log1p` avoids cancellation near `b*n=0`. A failed fit gives an exception rather than an apparently successful `FitResult`.

## Chronological holdout

`temporal_holdout_scores` sorts observations by cycle, keeps equal-cycle observations on one side, scores later observations against fits trained only on earlier cycles, and separates the held-out score from the full-data post-selection refit in `select_model_by_validation`. The audit patch rejects 2D arrays that were silently flattened. New future-knee and independent RMSE regression checks exercise that contract. No independent-cell holdout or multi-regime transfer claim is made.

## EOL and uncertainty

`FitResult.eol_cycle` now uses continuous `brentq` root solving, evaluating endpoints first, on [0, 3 × max observed cycle], and returns `None` if no within-cap crossing occurs. This replaces grid quantization; results outside the horizon are right-censored by policy. `bootstrap_life_projection` uses centered-residual refits with fixed-seed RNG, counts requested, finite EOL, censored, and failed draws, and withholds interval bounds whenever censoring or failure occurs. Its `successful_samples` is the finite-EOL count; successful solver fits including censored ones = `successful_samples + censored_samples`. Do not present these conditional intervals as calibrated unconditional confidence bounds.

## Thermal convention

The function interface uses Celsius `temperature_c` and `reference_c`, explicitly converts to Kelvin, and expects activation energy in eV with Boltzmann constant 8.617333262e-5 eV/K. AF = exp[(Ea/kB)(1/Tref - 1/T)]. Negative activation energy now rejected; extreme over/underflow rejected. Temperature effect is an illustrative factor, not jointly inferred from empirical cycle histories.

## Oxford measured EFC and data provenance

`equivalent_full_cycles` integrates positive (discharge) current over measured seconds using trapezoids, divides ampere-hours by nominal cell Ah, and does not double-count charging. Its clipping/interpolation convention must be kept explicit. Offline fixture tests pass; six real-data ORA integration cases remain skipped and cannot certify measured-data results. See `NUMERICAL_VALIDATION.md` and `DATA_SCHEMA_REPORT.md`.

## Scope limits

No field deployment, independent chemistry dataset validation, parameter-uncertainty calibration, or observational trial was performed; the website's exponential teaching curve is not the native fitted engine.
