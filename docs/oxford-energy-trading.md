---
layout: default
title: Oxford Grid-Battery Real-Data Example
---

# Oxford grid-battery real-data example

This opt-in example applies the bcla workflow to the University of Oxford's
energy-trading battery degradation dataset. The source contains one year of
operation for six 16 Ah lithium-ion cells following three grid-trading control
strategies, with per-cell current profiles and 13 capacity checks per cell.

The repository does not bundle, mirror, or relicense the dataset. The example
downloads original files from the Oxford Research Archive at runtime.
Each download is capped at 32 MiB before decoding; the largest official profile
was 8.87 MiB during the 2026-08-31 audit. A larger response is rejected rather
than read into memory without a bound.

- Official dataset record:
  `https://ora.ox.ac.uk/objects/uuid:9aae61af-2949-49f1-8ad5-6aea448979e5`
- Dataset DOI: `10.5287/bodleian:gJPdDzvP4`
- Data license: ODC Open Database License (ODbL) 1.0; individual contents are
  covered by the Database Contents License (DbCL) 1.0.

## Run it

From an installed source checkout:

```bash
python examples/oxford_energy_trading.py --cell BMR_cell1
```

To save a diagnostic figure or disable the residual bootstrap:

```bash
python examples/oxford_energy_trading.py \
  --cell BMR_cell1 \
  --bootstrap-samples 0 \
  --output oxford_bmr_cell1.png
```

The six supported cell IDs are `BMP_cell1`, `BMP_cell2`, `BMR_cell1`,
`BMR_cell2`, `SPM_cell1`, and `SPM_cell2`.

## Converting measured current to EFC

The capacity files report `profile_time_s` and `capacity_Ah`; they do not report
a laboratory cycle index. Relabeling elapsed time as cycle count would be
misleading. The example instead aligns each capacity check with its cell's
measured `time_s,current_A` profile and estimates cumulative discharge
equivalent full cycles:

```text
EFC(t) = integral(max(I(t), 0) dt) / (3600 * Q_nominal)
```

Positive current is discharge in the source data, negative current is charge,
and `Q_nominal` is the stated 16 Ah cell capacity. Charging samples are clipped
to zero before trapezoidal integration. The result is discharge-throughput EFC,
not elapsed days, commanded cycles, or a count of laboratory charge/discharge
procedures.

The official files contain a small number of duplicate or reversed profile-time
rows. The example makes its repair observable: it stable-sorts profile time,
averages current at identical timestamps, and prints the number of affected
transitions and duplicate samples. Each final capacity check also trails the
last near-zero-current sample by less than 1,004 seconds. The example caps that
small tail to the last observation only when the gap is at most 1,800 seconds
and the last absolute measured current is at most 1 mA; it prints the gap.
Only that single final capacity check may be capped. Anything outside those
conditions is rejected.

Saved figures relabel the horizontal axis as `Measured Discharge EFC`; they do
not present this throughput estimate as a laboratory cycle count. Solid lines
cover the observed window and dashed lines show only the bounded projection to
EOL, or to the three-times-observed limit when EOL is unsupported. The console
output states the chronological training/holdout sizes and reports bounded EOL,
RUL, and bootstrap censoring diagnostics explicitly.

## Live source audit

The following values were reproduced from the original ORA files on
2026-08-31 using the same canonicalization and integration code:

| Cell | Capacity checks | Measured discharge EFC | Final retention |
| --- | ---: | ---: | ---: |
| BMP cell 1 | 13 | 412.37 | 97.53% |
| BMP cell 2 | 13 | 410.12 | 97.56% |
| BMR cell 1 | 13 | 1558.15 | 85.97% |
| BMR cell 2 | 13 | 1557.65 | 85.15% |
| SPM cell 1 | 13 | 689.23 | 98.35% |
| SPM cell 2 | 13 | 689.93 | 98.23% |

The measured EFC is lower than an estimate from commanded schedules because
the tester enforced voltage limits and entered constant-voltage operation when
necessary. That is why the measured per-cell current files are primary here.

## Interpretation limits

- EFC integration is approximate because logging was irregular and samples
  were not guaranteed exactly at current transitions.
- Thirteen monthly capacity checks provide a compact demonstration, not broad
  forecast validation or independent-cell cross-validation.
- The 20% chronological holdout contains three observations. Report that small
  sample alongside every validation score.
- Bounded EOL can be unsupported, and bootstrap replicates can be censored.
  The example prints those outcomes instead of dropping them.
- The empirical fits do not model electrochemistry, cell safety, dispatch, or
  future protocol changes.

## Citation

When using the data, follow the archive's attribution and ODbL/DbCL terms and
cite the dataset:

Reniers, J. M., Mulder, G., and Howey, D. A. (2020). *Oxford energy trading
battery degradation dataset*. University of Oxford.

The source readme also requests citation of the related work, including:

Reniers, J. M., Mulder, G., and Howey, D. A. "Improving optimal control of
grid-connected lithium-ion batteries through more accurate battery and
degradation modelling." *Journal of Power Sources* 379 (2018), 91-102.
[`10.1016/j.jpowsour.2018.01.004`](https://doi.org/10.1016/j.jpowsour.2018.01.004)
