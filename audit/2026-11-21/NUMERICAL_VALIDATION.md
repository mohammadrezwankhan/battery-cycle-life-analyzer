# Independent analytical validation and evidence

## Continuous EOL reference

For the synthetic linear curve `Q(n)=1-0.17n`, threshold `0.8Q0`, observed maximum `n=1`: exact `n_EoL=0.2/0.17 = 1.1764705882352942`. Old 100,000-point search on [0,3] returned `1.1764917649176492`; absolute discretization error `2.1176682355e-5` cycles. The new `brentq` regression test requires absolute error at most `1e-10`. At `k=0.01`, the crossing `n=20` is outside [0,3], so the correct result is `None` (right-censored).

## Independent nonlinear references

Power: `Q(n)=1-0.01n^0.6`, `n_EoL=(0.2/0.01)^(1/0.6)=147.3612599456155` cycles. Log: `Q(n)=1-0.05 ln(1+0.001n)`, `n_EoL=expm1(0.2/0.05)/0.001=53598.15003314424` cycles. Both are within chosen synthetic observation horizons, and tests compare solver roots to analytical references (relative tolerance 1e-9). For `bn=1e-16`, `log1p(bn)` retains a nonzero first-order term that `log(1+bn)` loses.

## Independently calculated thermal values

With `Ea=0.5 eV`, `Tref=25 °C`, `kB=8.617333262e-5 eV/K`: AF(0 °C)=`0.16844390324263317`; AF(25 °C)=`1.0`; AF(45 °C)=`3.398646162285684`. These are analytical arithmetic examples, not battery observations.

## Measured-current EFC arithmetic test fixture

At `time_s=[0,1800,3600]`, `current_A=[2,2,-2]`, and `nominal_capacity_Ah=3`, clipped discharge current=[2,2,0]. Integrated discharge from 0 to 3600 s is 1.5 Ah, so EFC=0.5. At t=2700 s, EFC=(1 Ah + 0.375 Ah)/3 Ah=0.4583333333333333. This validates the documented *clipped-then-interpolated* convention, not continuous sign-crossing integration of the raw current.

## Chronology and bootstrap

Late-window RMSE is independently recalculated from the training-only fitted model's later predictions in the regression tests. Random-state repeatability, all-draw accounting and censored-bound suppression already have tests in `tests/test_core.py`. Fixed-seed reproducibility does not establish heteroscedastic/serial correlation validity; no stochastic coverage claim is added.

## Reproducibility

Run `python -m pytest -v tests/test_scientific_hardening.py tests/test_core.py tests/test_equivalent_full_cycles.py` and `python -m pytest -q -rs` from a wheel or editable checkout. Baseline evidence: https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44869544391 ; red phase: https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44944259925 ; first corrected suite: https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44944454660 . These source-independent constants are deterministic formulas, not observed benchmark results.

## Independent official-source EFC recheck (4/6 cells)

The official Oxford Research Archive record is `https://ora.ox.ac.uk/objects/uuid:9aae61af-2949-49f1-8ad5-6aea448979e5` (DOI: 10.5287/bodleian:gJPdDzvP4, ODbL/DbCL terms). A second analytical implementation used raw archive profile CSV text, stable cycle/time sorting, mean current for duplicate times, clipping negative discharge current to zero at measurement samples, trapezoidal integration in seconds, division by 16 Ah, and the documented near-zero-current final-tail cap. The four rows in `OXFORD_MEASURED_RECHECK.md` match the existing test references within 0.01 EFC and 1e-6 normalized retention. This is source-based arithmetic, not an external-fitted-model performance benchmark; BMR cells remain unverified and the six automated live integration tests are still skipped. No data redistributed.
