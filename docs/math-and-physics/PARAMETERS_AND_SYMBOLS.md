# Parameters, symbols and units

## Native fitting coordinates

| Symbol / code field | Meaning and unit | Source constraint/default |
| --- | --- | --- |
| $n$, `cycles` | Cycle coordinate; may represent cycles or explicitly derived discharge EFC | Finite, nonnegative for fitting; caller owns coordinate meaning |
| $q$, `capacity` | Capacity, normally normalized fraction | Fitter does not normalize; `Q0` bounds imply a scale near 1 |
| `Q0` | Fitted capacity at coordinate zero, same unit as $q$ | [.5, 1.5]; guess max observed capacity |
| `k` | Linear fade per cycle/EFC | [0, 1]; unit $q/n$ |
| `α`, `β` | Power-law scale and exponent | α [0, 5], unit $q/n^\beta$; β [.1, 2], dimensionless |
| `a`, `b` | Logarithmic amplitude and inverse coordinate | a [0, 1], unit $q$; b [0, 100000], unit $n^{-1}$ |
| `pcov` | Approximate parameter covariance matrix | Registry parameter order; shape 2×2 or 3×3, mixed parameter units |
| `rmse`, `r_squared` | Root mean square residual / explained-variance diagnostic | RMSE in capacity units; R² dimensionless |
| `validation_fraction` | Requested late observation-row fraction | .2, in (0, 1); actual group-aware split can differ |
| `split_cycle` | First held-out cycle coordinate | Stored on `ValidationScore` with `train_size` and `validation_size` |
| `eol_fraction` | Threshold divided by fitted initial capacity | .8, in (0, 1) |
| `current_cycle` | RUL reference coordinate | Default maximum observed cycle; nonnegative finite |
| `confidence`, `samples`, `random_state` | Bootstrap quantile coverage, replicate count, RNG seed | .95, 500, `None`; explicit examples set seed 42 |

[bcla/core.py:38–173](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L38-L173) [bcla/core.py:179–241](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L179-L241) [bcla/core.py:299–404](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L299-L404) [bcla/core.py:407–533](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L407-L533)

## Experimental metadata and EFC

| Field | Unit / interpretation |
| --- | --- |
| `time_s`, `query_time_s` | Seconds, measured range; query order is retained |
| `current_a` | A; positive discharge, negative charge clipped at samples |
| `nominal_capacity_ah` | Positive Ah; Oxford default 16 Ah |
| `temperature_c` | °C metadata; loader requires finite values, not a physical temperature envelope |
| `c_rate` | Nonnegative C-rate metadata; no automatic fitter coupling |
| `rest_time_h`, `cycles_per_day` | Hours / observation-segment aggregate cycling rate |
| `depth_of_discharge` | Fraction [0, 1] |
| `energy_throughput_wh` | Nonnegative Wh metadata; distinct from discharge EFC |
| `timestamp_iso`, interval start/end | ISO-parsed time strings; use a consistent timezone convention |
| `interval_seconds` | Positive interval duration computed by history loader |
| `schema_version`, history schema | Returned metadata tags, defaults `"1"` and `"2"` |

[bcla/datasets.py:74–203](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L74-L203) [bcla/datasets.py:352–576](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L352-L576) [bcla/datasets.py:746–923](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L746-L923) [examples/oxford_energy_trading.py:25–29](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L25-L29)

## Separate temperature and browser inputs

The native `arrhenius_acceleration_factor(temperature_c, reference_c=25.0, activation_ev=0.5)` uses Celsius inputs converted to Kelvin and eV activation energy. Its Boltzmann constant is `8.617333262e-5 eV/K`. [bcla/core.py:539–566](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L539-L566)

| Browser degradation input | Default | Accepted parameter range | Unit |
| --- | --- | --- | --- |
| `fadePer1000Pct` | 18 | 2–40, UI step 1 | Displayed `% / 1k cycles`; exponential coefficient input |
| `temperatureC` | 25 | 10–50, step 1 | °C |
| `cRate` | 1 | .2–3, step .1 | C |
| `initialCapacityAh` | 100 | 10–200, step 5 | Ah |

The evaluator clamps finite numeric inputs to these bounds and substitutes defaults for missing/nonfinite values. UI steps do not quantize programmatic API values. Browser time clamps to 0–1000 cycles. These are display/model-domain limits, not experimentally validated cell operating limits. [docs/index.html:183–189](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L183-L189) [docs/index.html:239–254](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L239-L254)
