# Native declaration catalog

This catalog records the 36 source-defined public declarations in the six native modules, including 48 declared dataclass fields. It is an exact source snapshot, not a compatibility promise. Decorator-inclusive links retain the dataclass/property contract; separate definition coordinates remain in the operational inventory. See [API contracts](API_CLI_AND_INTERFACES.md) for shapes, units, exceptions and write behavior. Imported third-party names and private/test/security helpers are not advertised as native user APIs.

Functions and methods below preserve positional/keyword markers and defaults. Dataclass field listings describe generated constructor inputs; `field(default_factory=...)` is a per-instance factory. Frozen containers do not recursively freeze their lists, dictionaries or arrays.

## `bcla/__main__.py`

### `main`

[bcla/__main__.py:9–174](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/__main__.py#L9-L174)

```python
main() -> None
```


## `bcla/core.py`

### `FitResult`

[bcla/core.py:57–125](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L57-L125)

```python
@dataclass
class FitResult:
    model_name: str
    params: dict[str, float]
    pcov: np.ndarray
    rmse: float
    r_squared: float
    cycles: np.ndarray
    observed: np.ndarray
    predicted: np.ndarray
```

### `FitResult.project`

[bcla/core.py:70–84](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L70-L84)

```python
project(self, target_cycles: float) -> float
```

### `FitResult.eol_cycle`

[bcla/core.py:86–111](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L86-L111)

```python
eol_cycle(self, eol_fraction: float=0.8) -> Optional[float]
```

### `FitResult.summary`

[bcla/core.py:113–125](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L113-L125)

```python
summary(self, *, ascii_only: bool=False) -> str
```

### `ValidationScore`

[bcla/core.py:128–137](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L128-L137)

```python
@dataclass(frozen=True)
class ValidationScore:
    model_name: str
    rmse: float
    r_squared: float
    train_size: int
    validation_size: int
    split_cycle: float
```

### `ModelSelection`

[bcla/core.py:140–153](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L140-L153)

```python
@dataclass
class ModelSelection:
    model_name: str
    fit: FitResult
    scores: dict[str, ValidationScore]
    criterion: Literal['rmse', 'r_squared']
    validation_fraction: float
```

### `ModelSelection.validation_score`

[bcla/core.py:150–153](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L150-L153)

```python
@property
validation_score(self) -> ValidationScore
```

### `LifeProjectionInterval`

[bcla/core.py:156–173](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L156-L173)

```python
@dataclass(frozen=True)
class LifeProjectionInterval:
    model_name: str
    confidence: float
    eol_fraction: float
    current_cycle: float
    eol_estimate: Optional[float]
    eol_lower: Optional[float]
    eol_upper: Optional[float]
    rul_estimate: Optional[float]
    rul_lower: Optional[float]
    rul_upper: Optional[float]
    requested_samples: int
    successful_samples: int
    censored_samples: int
    failed_samples: int
```

### `fit_capacity_fade`

[bcla/core.py:179–258](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L179-L258)

```python
fit_capacity_fade(cycles: ArrayLike, capacity: ArrayLike, model: str='power_law', q0_guess: Optional[float]=None) -> FitResult
```

### `fit_all_models`

[bcla/core.py:261–263](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L261-L263)

```python
fit_all_models(cycles: np.ndarray, capacity: np.ndarray) -> dict[str, FitResult]
```

### `best_model`

[bcla/core.py:266–274](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L266-L274)

```python
best_model(results: dict[str, FitResult], criterion: Literal['rmse', 'r_squared']='rmse') -> tuple[str, FitResult]
```

### `temporal_holdout_scores`

[bcla/core.py:299–364](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L299-L364)

```python
temporal_holdout_scores(cycles: ArrayLike, capacity: ArrayLike, validation_fraction: float=0.2) -> dict[str, ValidationScore]
```

### `select_model_by_validation`

[bcla/core.py:367–404](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L367-L404)

```python
select_model_by_validation(cycles: ArrayLike, capacity: ArrayLike, validation_fraction: float=0.2, criterion: Literal['rmse', 'r_squared']='rmse') -> ModelSelection
```

### `bootstrap_life_projection`

[bcla/core.py:407–533](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L407-L533)

```python
bootstrap_life_projection(result: FitResult, eol_fraction: float=0.8, current_cycle: Optional[float]=None, confidence: float=0.95, samples: int=500, random_state: Optional[int]=None) -> LifeProjectionInterval
```

### `arrhenius_acceleration_factor`

[bcla/core.py:539–566](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L539-L566)

```python
arrhenius_acceleration_factor(temperature_c: float, reference_c: float=25.0, activation_ev: float=0.5) -> float
```


## `bcla/datasets.py`

### `synthetic_lfp`

[bcla/datasets.py:17–53](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L17-L53)

```python
synthetic_lfp(cycles: int=1500, seed: int=42, noise_std: float=0.005) -> tuple[NDArray[np.float64], NDArray[np.float64]]
```

### `synthetic_nmc`

[bcla/datasets.py:56–71](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L56-L71)

```python
synthetic_nmc(cycles: int=1000, seed: int=7, noise_std: float=0.004) -> tuple[NDArray[np.float64], NDArray[np.float64]]
```

### `equivalent_full_cycles`

[bcla/datasets.py:108–203](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L108-L203)

```python
equivalent_full_cycles(time_s: Any, current_a: Any, nominal_capacity_ah: float, *, query_time_s: Any | None=None) -> NDArray[np.float64]
```

### `LongFormCycleData`

[bcla/datasets.py:206–262](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L206-L262)

```python
@dataclass(frozen=True)
class LongFormCycleData:
    rows: list[dict[str, Any]]
    schema_version: str
    validation_envelopes: dict[str, dict[str, Any]]
    duty_cycle_history: list[dict[str, Any]] = field(default_factory=list)
    duty_cycle_history_schema: str | None = None
    duty_cycle_history_validation: dict[str, dict[str, Any]] = field(default_factory=dict)
```

### `LongFormCycleData.cell_ids`

[bcla/datasets.py:217–225](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L217-L225)

```python
@property
cell_ids(self) -> tuple[str, ...]
```

### `LongFormCycleData.cycles`

[bcla/datasets.py:227–238](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L227-L238)

```python
@property
cycles(self) -> NDArray[np.float64]
```

### `LongFormCycleData.capacity`

[bcla/datasets.py:240–251](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L240-L251)

```python
@property
capacity(self) -> NDArray[np.float64]
```

### `LongFormCycleData.for_cell`

[bcla/datasets.py:253–262](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L253-L262)

```python
for_cell(self, cell_id: str) -> tuple[NDArray[np.float64], NDArray[np.float64]]
```

### `load_duty_cycle_history`

[bcla/datasets.py:445–576](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L445-L576)

```python
load_duty_cycle_history(csv_path: str | Path, sep: str | None=None, schema_version: str='2', *, expected_cell_ids: set[str] | None=None) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], str]
```

### `load_cycle_data`

[bcla/datasets.py:653–743](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L653-L743)

```python
load_cycle_data(csv_path: str | Path, cycle_col: str='cycle', capacity_col: str='capacity', sep: str | None=None, normalize: bool=True) -> tuple[NDArray[np.float64], NDArray[np.float64]]
```

### `load_cycle_data_long_form`

[bcla/datasets.py:746–923](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L746-L923)

```python
load_cycle_data_long_form(csv_path: str | Path, sep: str | None=None, normalize: bool=True, schema_version: str='1', history_csv_path: str | Path | None=None, history_schema_version: str='2') -> LongFormCycleData
```


## `bcla/viz.py`

### `capacity_fade`

[bcla/viz.py:52–125](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/viz.py#L52-L125)

```python
capacity_fade(result: FitResult, ax: Optional[Axes]=None, show_eol: bool=True, eol_fraction: float=0.8, title: str='Capacity Fade') -> Axes
```

### `model_comparison`

[bcla/viz.py:128–150](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/viz.py#L128-L150)

```python
model_comparison(results: dict[str, FitResult], eol_fraction: float=0.8) -> Figure
```

### `eol_vs_temperature`

[bcla/viz.py:153–201](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/viz.py#L153-L201)

```python
eol_vs_temperature(q0: float, k: float, cycle_range: tuple[int, int]=(0, 3000), temperatures: Optional[list[float]]=None, eol_fraction: float=0.8, ax: Optional[Axes]=None) -> Axes
```


## `examples/oxford_energy_trading.py`

### `OxfordCellData`

[examples/oxford_energy_trading.py:42–54](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L42-L54)

```python
@dataclass(frozen=True)
class OxfordCellData:
    cell_id: str
    efc: NDArray[np.float64]
    capacity_ah: NDArray[np.float64]
    normalized_capacity: NDArray[np.float64]
    profile_rows: int
    canonical_profile_rows: int
    non_increasing_transitions: int
    duplicate_samples: int
    unobserved_tail_s: float
```

### `load_oxford_cell_from_text`

[examples/oxford_energy_trading.py:207–247](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L207-L247)

```python
load_oxford_cell_from_text(cell_id: str, profile_csv: str, capacity_csv: str, nominal_capacity_ah: float=NOMINAL_CAPACITY_AH) -> OxfordCellData
```

### `load_oxford_cell`

[examples/oxford_energy_trading.py:250–257](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L250-L257)

```python
load_oxford_cell(cell_id: str) -> OxfordCellData
```

### `run_analysis`

[examples/oxford_energy_trading.py:308–418](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L308-L418)

```python
run_analysis(cell_id: str, *, validation_fraction: float, bootstrap_samples: int, output: Path | None) -> None
```

### `main`

[examples/oxford_energy_trading.py:421–438](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L421-L438)

```python
main() -> None
```


## `examples/render_model_preview.py`

### `main`

[examples/render_model_preview.py:14–23](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/render_model_preview.py#L14-L23)

```python
main() -> None
```

## Package re-exports and operational surfaces

The package root re-exports `LongFormCycleData`, `equivalent_full_cycles`, `load_cycle_data`, `load_cycle_data_long_form` and `load_duty_cycle_history`. Fitting/visualization remain explicit submodules. The source runtime version is `0.2.0`; package metadata separately declares `0.3.0`. [bcla/__init__.py:15–31](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/__init__.py#L15-L31) [pyproject.toml:5–10](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L5-L10)

Operational entrypoints also include the notebook generator, portfolio validator, browser CSP command and repository security/quality tooling. All 376 Python class/function definitions and 24 parser registrations across 36 files are indexed separately, including conditional/nested helpers. Static extraction of security tooling is not a completed security audit. [Source accounting](../SOURCE_EVIDENCE.md) and [toolchain](../maintainer/TOOLCHAIN_AND_DEPENDENCY_MATRIX.md) state those limits.
