---
layout: default
title: Battery Cycle-Life Analyzer
---

# Battery Cycle-Life Analyzer

Fit transparent empirical capacity-fade models, compare diagnostics, and
project battery end of life inside an explicit extrapolation limit.

[View the source and documentation](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer)
|
[Open the Colab notebook](https://colab.research.google.com/github/mohammadrezwankhan/battery-cycle-life-analyzer/blob/main/notebooks/demo.ipynb)

![Linear, power-law, and logarithmic model comparison](model_comparison_preview.png)

## What it provides

- Linear, power-law, and logarithmic capacity-fade fits using SciPy.
- RMSE and R^2 diagnostics for every fitted model.
- A configurable EOL threshold relative to fitted initial capacity.
- A bounded projection horizon that returns no estimate when EOL is outside
  three times the observed cycle range.
- Reproducible synthetic LFP and NMC demonstrations.
- CSV/TSV cycle-capacity import with normalization and validation.
- Optional long-form ingestion with metadata columns for reproducibility and
  provenance.
- Publication-ready Matplotlib figures and a tested Python API.

## Quick start

```bash
git clone https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer.git
cd battery-cycle-life-analyzer
python -m pip install .
python -m bcla --model all
```

## Model families

For normalized capacity `Q(n)` at cycle `n`:

- Linear: `Q(n) = Q0 - k n`
- Power law: `Q(n) = Q0 - alpha n^beta`
- Logarithmic: `Q(n) = Q0 - a ln(1 + b n)`

The package reports fit diagnostics before selecting the lowest-RMSE model.
An in-window fit is not treated as proof of a trustworthy long-range forecast,
so unsupported threshold crossings return no estimate.

## Scope and limitations

This is an empirical research and educational baseline, not an
electrochemical, pack-safety, or production BMS model. The bundled data are
synthetic. Engineering conclusions require representative laboratory data and
explicit consideration of chemistry, protocol, temperature, time metadata, and
uncertainty.

## Project links

- [README and equations](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer#readme)
- [Contributing guide](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/main/CONTRIBUTING.md)
- [MIT license](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/main/LICENSE)
