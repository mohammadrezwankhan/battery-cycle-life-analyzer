# Browser model and control inventory

The active lesson kind is **`degradation`**. Its JavaScript runs independently of native Python and external measurements. Source `docs/index.html` bundles ten teaching model kinds; this review executed the eight configured degradation checkpoints and structurally enumerated the remaining kinds. Their presence is not a claim that this site exposes ten active lessons or that all ten models were numerically validated. [docs/index.html:155–238](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L155-L238)

## Pure exports and inputs

`LabSimulation` exports `MODEL_SPECS`, `getModelSpec(kind)`, `resolveParameters(kind, provided)`, `evaluateModel(kind, provided, time)` and `checkCheckpoint(checkpoint, metrics)`. An unknown kind throws. Parameter values must be finite JavaScript numbers; they are clamped to source bounds or replaced by defaults. UI steps do not quantize programmatic values. Time is clamped to the selected mode horizon, with nonfinite time replaced by zero. Metric output is a plain object. [docs/index.html:239–254](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L239-L254) [docs/index.html:328–344](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L328-L344)

Checkpoint comparisons accept `>=/gte`, `<=/lte`, `>/gt`, `</lt`, `==/=/eq/≈`. Nonfinite/unknown values or unsupported operators return status `invalid`; numerical comparison returns `pass` or `fail`. Absolute tolerance expands inclusive/equality comparisons, while strict inequalities ignore it. This verifies one formula fixture, not physical calibration. [docs/index.html:328–341](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L328-L341)

## Bundled model specs

| Kind | Model time / horizon | Input keys | Metric keys |
| --- | --- | --- | --- |
| `battery` | 6 h | `capacityAh`, `currentA`, `resistanceOhm`, `ambientC`, `initialSoc` | `socPct`, `voltageV`, `temperatureC`, `powerKW` |
| `thermal` | 60 min | `heatW`, `coolingWK`, `capacityJPerK`, `ambientC` | `temperatureC`, `heatRemovedW`, `storedEnergyKJ`, `residualW` |
| `degradation` | 1000 cycles | `fadePer1000Pct`, `temperatureC`, `cRate`, `initialCapacityAh` | `retentionPct`, `capacityAh`, `resistanceGrowthPct`, `throughputKWh` |
| `grid` | 24 h | `demandKW`, `solarKW`, `batteryKW`, `carbonGPerKWh` | `gridImportKW`, `solarOutputKW`, `renewablePct`, `emissionsKgPerH` |
| `cooling` | 60 min | `serverCount`, `utilizationPct`, `ambientC`, `coolingEfficiency` | `itKW`, `coolingKW`, `pue`, `inletC` |
| `agents` | 30 min | `arrivalRate`, `agentCount`, `serviceRate`, `coordinationPct` | `backlog`, `throughput`, `utilizationPct`, `waitMinutes` |
| `markets` | 24 h | `baseSpreadBps`, `feeBps`, `slippageBps`, `notionalUSD` | `spreadBps`, `netEdgeBps`, `netPnlUSD`, `costUSD` |
| `control` | 20 s | `setpoint`, `damping`, `naturalFrequency`, `gain` | `output`, `error`, `velocity`, `overshootPct` |
| `security` | 60 min | `alertRate`, `analystCount`, `reviewRate`, `automationPct` | `backlog`, `coveragePct`, `reviewedAlerts`, `workloadPct` |
| `charging` | 120 min | `capacityKWh`, `chargerKW`, `initialSoc`, `efficiencyPct` | `socPct`, `chargingKW`, `energyAddedKWh`, `lossKW` |

The active exponential equations, units and parameter bounds are described in [equations](../math-and-physics/EQUATIONS_AND_DERIVATIONS.md) and [symbols](../math-and-physics/PARAMETERS_AND_SYMBOLS.md). Each bundled specification also states its own teaching assumptions. No inactive mode is imported into the native empirical model registry. [docs/index.html:167–238](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L167-L238) [bcla/core.py:38–42](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L38-L42)

## Active checkpoint observations

| Module | Metric at model time | Observed value | Source expected / tolerance |
| --- | --- | --- | --- |
| `module-1` | `retentionPct` at 1000 cycles | 83.527021141 | == 83.527021 ± 0.02 |
| `module-1` | `capacityAh` at 1000 cycles | 83.527021141 | == 83.527021 ± 0.02 |
| `module-2` | `retentionPct` at 1000 cycles | 74.321505943 | == 74.321506 ± 0.02 |
| `module-2` | `capacityAh` at 1000 cycles | 74.321505943 | == 74.321506 ± 0.02 |
| `module-3` | `retentionPct` at 1000 cycles | 65.724664717 | == 65.724665 ± 0.02 |
| `module-3` | `throughputKWh` at 1000 cycles | 302.168154383 | == 302.168154 ± 0.02 |
| `module-4` | `retentionPct` at 1000 cycles | 90.483741804 | == 90.483742 ± 0.02 |
| `module-4` | `capacityAh` at 1000 cycles | 45.241870902 | == 45.241871 ± 0.02 |

These are actual Node evaluations of the exact source inline model script and canonical lesson configuration, whose embedded JSON was checked for equality. No DOM, canvas, download, storage, clipboard or assistive-technology interaction was executed. Lesson inputs and expectations are retained in [the pinned configuration](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/lesson-config.json).

## UI and file/state contracts

| Surface | Source-defined behavior |
| --- | --- |
| Main lab | Sliders update the current synthetic parameters; timeline controls model time; Run/Pause and reset affect animation state. The plotted/exported series has 241 evenly spaced samples including both endpoints. |
| Checkpoints | Presets choose lesson inputs and the first fixed checkpoint time; each check can use its own fixed time. A module completion record is in memory and denotes a prior verified experiment, not a native test. |
| CSV export | `battery-cycle-life-analyzer-synthetic-telemetry.csv`; time, metric and `input_` columns, numerical values formatted to 12 significant digits and CRLF rows. No measured data is imported. |
| Configuration dialog | Shows/downloads canonical embedded lesson JSON; clipboard API has a selection/copy fallback. |
| `LabDashboard` | Frozen wrapper exposes `getState()` with copied parameter values plus `evaluateModel` and `getModelSpec`; no native Python bridge. |
| Portfolio guide | Local-storage key includes repository and historical source revision; stores reviewed IDs, notes and motion preference. Study-plan export includes `execution_status: not_executed_by_this_guide`. |
| Native catalog | Text/tag filters combine search with all selected tags; copy buttons copy displayed commands with fallback selection. It does not execute them. |
| Animation archive | Gallery loads media after explicit play; waveform controls alter decorative drawing, not a battery simulation. |

[docs/index.html:350–427](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L350-L427) [docs/index.html:461–491](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L461-L491) [docs/portfolio/index.html:255–286](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/portfolio/index.html#L255-L286) [docs/native-lessons.html:83–131](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/native-lessons.html#L83-L131) [docs/animations/gallery.js:1–20](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/animations/gallery.js#L1-L20) [docs/animations/waveform.html:154–215](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/animations/waveform.html#L154-L215)

The existing browser pages retain their historical native/catalog provenance and original scripts, styling and configs. The handbook adds navigation and a dated current source explanation. Actual keyboard, responsive, storage/export and published-page checks belong to a supported browser review and remain unclaimed here.
