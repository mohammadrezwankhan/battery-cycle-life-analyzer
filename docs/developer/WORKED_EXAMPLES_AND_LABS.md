# Worked examples and laboratories

## 1. Reproduce the bundled synthetic CSV

Run this from the pinned checkout after setup. The file has twelve observations from cycle 0 through 1100; its 3 Ah starting value is normalized to 1 by the loader. These bundled observations are synthetic demonstrations, not measured validation data. [data/quickstart.csv:1–13](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/data/quickstart.csv#L1-L13) [README.md:185–188](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/README.md#L185-L188)

```python
from bcla import core, datasets

cycles, capacity = datasets.load_cycle_data("data/quickstart.csv")
selection = core.select_model_by_validation(cycles, capacity, validation_fraction=0.2)
fit = selection.fit
interval = core.bootstrap_life_projection(fit, samples=50, random_state=42)
print(selection.model_name)
print(round(selection.validation_score.rmse, 6))
print(round(fit.eol_cycle(0.8), 3))
print(interval.successful_samples, interval.censored_samples, interval.failed_samples)
```

Observed on the review environment: `linear`, held-out RMSE `0.00101`, EOL `1112.54` cycles and replicate counts `50 0 0`. The split has nine training and three validation observations. Full-data fitted `Q0≈0.999982906`, `k≈0.000179767`; the 50-replicate conditional 95% EOL interval was approximately `[1107.055,1121.512]` cycles. That leaves a point RUL of approximately `12.540` cycles at cycle 1100. These are executed synthetic-example results, not a precision guarantee or measured lifetime forecast. The implementation and scope are in the [equations](../math-and-physics/EQUATIONS_AND_DERIVATIONS.md). [bcla/core.py:299–404](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L299-L404) [bcla/core.py:407–533](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L407-L533)

The equivalent CLI was executed successfully with `--model all --bootstrap-samples 50` and an absolute quickstart CSV path; it wrote `bcla_demo.png` in an external output directory. For arbitrary inputs, check `fit.eol_cycle(...) is None` before rounding; this fixture produced a crossing, but the API does not promise one. [bcla/__main__.py:74–178](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/__main__.py#L74-L178)

## 2. Check the EFC interpolation convention

```python
from bcla.datasets import equivalent_full_cycles

efc = equivalent_full_cycles(
    [0.0, 900.0], [8.0, -8.0], nominal_capacity_ah=16.0,
    query_time_s=[450.0, 900.0],
)
print(efc)  # [0.046875 0.0625]
```

This executed result integrates the line from sampled clipped currents `[8,0]`. Integrating a line through signed currents `[8,-8]` and clipping at its zero crossing would produce a different area. Choose and report the source convention when comparing an external EFC calculation. No charge throughput is counted, and cumulative EFC starts at zero at the first provided measurement. [bcla/datasets.py:108–203](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L108-L203)

## 3. Keep metadata with one cell

```python
from bcla.datasets import load_cycle_data_long_form

data = load_cycle_data_long_form(
    "data/cycle_metadata_example.csv",
    history_csv_path="data/cycle_duty_history_example.csv",
)
print(data.cell_ids)  # ('LFP-A', 'NMC-B')
x, q = data.for_cell("LFP-A")
```

The parsed fixture contains six observation rows and four history intervals, with history schema tag `"2"`. Each cell has only three observations; do not feed this tiny schema example to the six-distinct-cycle validation route and mistake an expected rejection for a loader failure. The metadata is retained, not coupled to an aging model. [data/cycle_metadata_example.csv:1–7](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/data/cycle_metadata_example.csv#L1-L7) [data/cycle_duty_history_example.csv:1–5](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/data/cycle_duty_history_example.csv#L1-L5) [bcla/core.py:277–296](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L277-L296)

## 4. Notebook and external-data boundary

All seven exact code cells in [the existing notebook](../../notebooks/demo.ipynb) were executed sequentially under Python with Matplotlib's Agg backend, in an external directory. The source notebook remained unmodified with empty outputs. Three figures were written. This verifies code-cell execution, not a Jupyter frontend, Colab install or interactive display. Its NMC seed-7 example selected `power_law`, reported held-out RMSE about `.00366`, EOL about `1071` cycles and a 100-replicate interval approximately `1066–1075` cycles. The displayed LFP/NMC comparison remains an illustrative comparison between generators. [build_notebook.py:70–179](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/build_notebook.py#L70-L179) [build_notebook.py:181–260](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/build_notebook.py#L181-L260)

The [Oxford walkthrough](../oxford-energy-trading.md) records a historical live-data audit dated 2026-08-31. This review ran its offline tests and CLI help, but did not download the external archive or rerun its six live cases. Before a fresh measured-data study, retain the actual input files, hashes, archive identity/license, canonicalization counts, EFC convention, holdout split and failed/censored outcomes. [docs/oxford-energy-trading.md:9–33](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/oxford-energy-trading.md#L9-L33) [examples/oxford_energy_trading.py:207–257](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L207-L257) [tests/test_oxford_live.py:1–48](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/tests/test_oxford_live.py#L1-L48)
