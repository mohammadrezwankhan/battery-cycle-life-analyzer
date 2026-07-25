# Battery Cycle‑Life Analyzer (bcla)

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![Tests](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/workflows/tests.yml/badge.svg)](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mohammadrezwankhan/battery-cycle-life-analyzer/blob/main/notebooks/demo.ipynb)

**Fit degradation models to battery cycling data, project remaining useful
life, and generate publication‑ready figures — in under 20 lines of Python.**

Designed for battery researchers, energy‑storage engineers, and students who
need a quick, transparent estimate of cycle‑life without running complex
physics simulations.

---

## Installation

Requires Python 3.9 or newer. Runtime dependencies are NumPy, SciPy, and
Matplotlib; `pip` installs them automatically.

```bash
git clone https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer.git
cd battery-cycle-life-analyzer
python -m pip install .
```

For an editable development installation with pytest:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Quick start

```bash
python -m bcla --model all
```

Or open [`notebooks/demo.ipynb`](notebooks/demo.ipynb) for an interactive walk‑through.

You can also point the CLI at a CSV/TSV file:

```bash
python -m bcla --csv data/cycles.csv --model all
python -m bcla --csv data/cycles.tsv --model all
```

Expected CSV/TSV columns (case sensitive):

- `cycle`: cycle index (int/float)
- `capacity`: measured capacity (absolute values; normalized internally by default)

Files ending in `.tsv` or `.tab` use a tab delimiter automatically. CLI column
mapping and separators are customizable; `\t` is accepted as an escaped tab:

```bash
python -m bcla --csv data/raw.txt --cycle-col n --capacity-col q --sep '\t' --no-normalize
```

## Long-form data schema (v1)

For provenance-aware workflows, use
`load_cycle_data_long_form()` to keep protocol metadata alongside `(cycle, capacity)`:

```python
from bcla.datasets import load_cycle_data_long_form

dataset = load_cycle_data_long_form("data/cycle_metadata_example.csv")
for cell_id in dataset.cell_ids:
    cycles, capacity = dataset.for_cell(cell_id)
    print(cell_id, cycles[:3], capacity[:3])
```

Required columns:

- `cell_id`
- `cycle`
- `capacity`

Optional experimental context columns:

- `chemistry`
- `timestamp_iso` *(RFC 3339 / ISO 8601 string, optional)*
- `temperature_c`
- `c_rate` *(non-negative)*
- `rest_time_h` *(non-negative)*
- `cycles_per_day` *(non-negative)*
- `depth_of_discharge` *(non-negative, fraction 0–1)*
- `energy_throughput_wh` *(non-negative)*
- `duty_cycle_profile` *(optional free-form descriptor, e.g. ``continuous``, ``1x daily``, ``partial cycles``)*
- `protocol`
- `source`

`cycles_per_day` is an aggregate summary for the exported trace segment and can be
non-integer (for example, `0.5` for one cycle every two days). If your lab workflow
explicitly alternates single and double cycles, keep the aggregate rate here and
capture the regime in `protocol`.

Every optional field is explicit: when a value is missing in a row, it is stored
as `None` rather than silently defaulted.

The loader validates:

- `cycle` and `capacity` must parse as finite numbers
- `cycle` and numeric optional fields (when provided) must be within their
  documented bounds:
  - `depth_of_discharge`: `0 <= value <= 1`
  - `c_rate`, `rest_time_h`, `cycles_per_day`, `energy_throughput_wh`:
    non-negative
- `cell_id`, `cycle`, `capacity` cannot be missing
- per-cell summary envelopes (`validation_envelopes`) including:
  - observed `cycle_range` and `cycle_count`
  - `timestamp_range` and `timestamp_span_days` when timestamps are present
  - min/max for `temperature_c`, `c_rate`, `rest_time_h`, `cycles_per_day`,
    `depth_of_discharge`, and `energy_throughput_wh`

Returned fields:

- `rows`: full observation list with all preserved metadata
- `schema_version`: schema tag (default `"1"`)
- `validation_envelopes`: structured per-cell metadata envelope
- `cycles` / `capacity`: convenience aliases for single-cell files
- `for_cell(cell_id)`: per-cell arrays for fitting existing API

The empirical fitting API remains unchanged:

```python
from bcla import core, datasets

dataset = datasets.load_cycle_data_long_form("data/cycle_metadata_example.csv")
cycles, capacity = dataset.for_cell("LFP-A")
results = core.fit_all_models(cycles, capacity)
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Degradation models** | Linear, power‑law (LFP‑style), logarithmic — all with scipy curve_fit |
| **Automatic best‑fit** | `bcla.core.best_model()` picks the lowest‑RMSE model |
| **EOL projection** | `FitResult.eol_cycle()` estimates when capacity hits any threshold |
| **Temperature acceleration** | Arrhenius‑based `arrhenius_acceleration_factor()` to compare operating temperatures |
| **Publication plots** | Matplotlib figures with ready‑to‑save PNG output at 150+ DPI |
| **Built‑in datasets** | Synthetic LFP and NMC cycling data for instant demo |
| **CSV/TSV import** | Load external cycle-capacity tables with normalization and validation |
| **CLI + Python API** | Use from the terminal or import as a library |

---

## Example

```python
from bcla import core, viz, datasets

# 1. Load data
cycles, capacity = datasets.synthetic_nmc(cycles=1000)

# Or load cycle-capacity data from a file
# cycles, capacity = datasets.load_cycle_data("data/cycles.csv")

# 2. Fit all models
results = core.fit_all_models(cycles, capacity)
name, best = core.best_model(results)                # picks lowest RMSE

# 3. Project end‑of‑life
eol = best.eol_cycle(eol_fraction=0.8)
print(f"Best model: {name}")
print(f"Projected EOL: {eol:.0f} cycles" if eol is not None
      else "EOL is outside the supported projection window")

# 4. Plot
fig = viz.model_comparison(results)
fig.savefig("capacity_fade.png", dpi=150, bbox_inches="tight")
```

Remaining useful life at the latest observed cycle is the projected EOL cycle
minus that cycle:

```python
current_cycle = cycles[-1]
rul_cycles = None if eol is None else max(0.0, eol - current_cycle)
print(f"Projected RUL: {rul_cycles:.0f} cycles" if rul_cycles is not None
      else "EOL is outside the supported projection window")
```

![Model comparison preview](docs/model_comparison_preview.png)

---

## How the models are calculated

The input capacity should be normalized, so an undegraded cell is near
`Q = 1`. For cycle index `n`, the library fits three empirical models:

| Model | Capacity equation | Parameters |
|-------|-------------------|------------|
| Linear | `Q(n) = Q0 - k n` | Initial capacity `Q0`; fade rate `k` |
| Power law | `Q(n) = Q0 - alpha n^beta` | Scale `alpha`; exponent `beta` |
| Logarithmic | `Q(n) = Q0 - a ln(1 + b n)` | Scale `a`; rate parameter `b` |

`scipy.optimize.curve_fit` estimates the parameters with bounded nonlinear
least squares. The initial-capacity bound is `0.5 <= Q0 <= 1.5`; all
degradation coefficients are constrained to non-negative values. The power-law
exponent is constrained to `0.1 <= beta <= 2.0`.

For observations `Q_i` and fitted values `Qhat_i`, model quality is reported as:

```text
RMSE = sqrt(mean((Q_i - Qhat_i)^2))
R^2  = 1 - sum((Q_i - Qhat_i)^2) / sum((Q_i - mean(Q))^2)
```

`best_model()` selects the lowest-RMSE fit by default. `eol_cycle(0.8)` then
finds the first projected cycle where `Q(n) <= 0.8 Q0`. To avoid presenting
unbounded extrapolation as evidence, the search stops at three times the
largest observed cycle and returns `None` if the threshold is not reached.

Temperature comparisons use a relative Arrhenius acceleration factor:

```text
AF = exp[(Ea / kB) (1 / Tref - 1 / T)]
```

where temperatures are in kelvin, `Ea` is activation energy in electron-volts,
and `kB` is the Boltzmann constant in eV/K. `AF > 1` indicates faster
degradation than at the reference temperature.

### Assumptions and limitations

- These are empirical curve fits, not electrochemical or safety models.
- The bundled LFP and NMC datasets are synthetic demonstrations.
- EOL projections are sensitive to data quality, model choice, and the
  extrapolation distance.
- The current release does not calculate parameter confidence intervals or
  propagate measurement uncertainty into RUL.
- The Arrhenius utility compares temperature acceleration independently; it is
  not coupled to the fitted capacity-fade trajectory.

Use laboratory data representative of the cell, protocol, temperature, and
operating window before drawing engineering conclusions.

---

## Project structure

```
battery-cycle-life-analyzer/
├── bcla/                    # Python library
│   ├── __init__.py
│   ├── core.py              # Degradation models & curve fitting
│   ├── viz.py               # Matplotlib plotting helpers
│   ├── datasets.py          # Synthetic data and CSV/TSV import
│   └── __main__.py          # CLI entry point
├── notebooks/
│   └── demo.ipynb           # Interactive Jupyter demo
├── tests/
│   ├── test_core.py         # Model and projection tests
│   └── test_datasets.py     # Data-import tests
├── .github/workflows/
│   └── tests.yml            # CI across supported Python versions
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── setup.py
├── Makefile
└── README.md
```

---

## When to use this vs. PyBaMM

| Tool | Best for |
|------|----------|
| **bcla** (this) | Quick capacity‑fade curve‑fitting from cycling test data; EOL estimates; temperature‑sensitivity studies |
| [PyBaMM](https://github.com/pybamm-team/PyBaMM) | Full physics‑based electrochemical battery simulation (DFN, SPMe, etc.) |

bcla is **complementary** — fit a model to PyBaMM output data, or use it standalone for lab‑test data.

---

## Contributing

Bug reports, focused feature proposals, documentation improvements, and
validation datasets with clear provenance are welcome. See
[CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, and pull-request
guidance.

---

## Citation

If you use this in published work, please cite the repository:

```bibtex
@software{khan2026bcla,
  author = {Mohammad Rezwan Khan},
  title = {Battery Cycle-Life Analyzer},
  year = {2026},
  url = {https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer}
}
```

---

## License

[MIT](LICENSE)
