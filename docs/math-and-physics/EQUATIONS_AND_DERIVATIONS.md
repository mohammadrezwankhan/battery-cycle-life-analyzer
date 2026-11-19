# Implemented equations and explanatory derivations

Let $n$ denote the supplied cycle coordinate and $q(n)$ the capacity on the caller's scale, normally a normalized fraction. For the Oxford adapter, $n$ is discharge EFC. The package does not convert a cycle count to calendar time or couple metadata to the fitted equations. These are empirical algebraic curves, not an electrochemical state model, ODE/PDE or pack-safety simulation. [bcla/core.py:18–42](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L18-L42) [bcla/datasets.py:206–262](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L206-L262) [examples/oxford_energy_trading.py:207–247](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L207-L247)

## 1. Three fitted families

| Registry name | Implemented equation | Bounds, in registry order |
| --- | --- | --- |
| `linear` | $q(n)=Q_0-kn$ | $Q_0\in[.5, 1.5]$, $k\in[0, 1]$ |
| `power_law` | $q(n)=Q_0-\alpha n^\beta$ | $Q_0\in[.5, 1.5]$, $\alpha\in[0, 5]$, $\beta\in[.1, 2]$ |
| `logarithmic` | $q(n)=Q_0-a\ln(1+bn)$ | $Q_0\in[.5, 1.5]$, $a\in[0, 1]$, $b\in[0, 10^5]$ |

All three have the fitted intercept $q(0)=Q_0$. There is no independently imposed physical initial condition or spatial boundary condition. On nonnegative $n$, their permitted fade coefficients produce nonincreasing curves, including constant curves when a required coefficient is zero. This is a mathematical property of the chosen formulas/bounds, not evidence of physical calibration. [bcla/core.py:18–42](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L18-L42)

For a positive threshold fraction $f<1$, the following continuous roots are **explanatory derivations**, not the implemented EOL algorithm:

$$n_f=\frac{Q_0(1-f)}{k},\qquad
n_f=\left(\frac{Q_0(1-f)}{\alpha}\right)^{1/\beta},\qquad
n_f=\frac{\exp(Q_0(1-f)/a)-1}{b}.$$

These expressions require positive denominators/coefficient combinations; zero fade may have no finite crossing. The exponential expression can overflow. Do not substitute the formulas for the source's explicit finite-window and finite-value checks. [bcla/core.py:86–111](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L86-L111)

## 2. Fitting and diagnostics

The source calls `curve_fit` with parameter bounds and `maxfev=50_000`. It supplies no weights, analytic Jacobian, solver method or uncertainty scale. Its initial guess is `Q0=max(y)` unless provided; linear $k$ uses the first/last input rows with a $10^{-6}$ denominator offset and floor $10^{-8}$; power-law starts at $(\alpha,\beta)=(.01,.6)$; logarithmic starts at $(a, b)=(.02,.1)$. Input rows are not sorted by this direct fit. [bcla/core.py:179–241](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L179-L241)

Under the [SciPy 1.17 `curve_fit` contract](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.curve_fit.html), bounds select default `trf`, absent `sigma` gives unweighted least squares, and the Jacobian is numerical. `pcov` is a local linear approximation with the default residual-based scaling, not a lifetime confidence interval. Optimization is local; model adequacy and identifiability require separate assessment.

For $N$ observations and residuals $r_i=y_i-\hat q(n_i)$, the stored diagnostics are

$$\mathrm{RMSE}=\sqrt{\frac{1}{N}\sum_i r_i^2},\qquad
R^2=1-\frac{\sum_i r_i^2}{\sum_i(y_i-\bar y)^2}.$$

The denominator in RMSE is $N$, not residual degrees of freedom. When observed variance is zero, training R² is stored as 0; held-out R² is NaN. These diagnostics describe the supplied arrays, not physical uncertainty. [bcla/core.py:243–258](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L243-L258) [bcla/core.py:339–364](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L339-L364)

## 3. Chronological validation and full-data refit

The validation route flattens arrays, stably sorts by cycle, and starts with $\max(2,\lceil Nv\rceil)$ late rows for requested fraction $v$. It moves the boundary to keep equal-cycle groups together and at least two distinct held-out cycle values. At least four distinct training cycle values are required for the current three-parameter maximum, with at least six distinct values overall. Each family is fitted only on earlier observations and scored on later ones. Selection then refits the chosen family to all sorted observations. [bcla/core.py:277–404](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L277-L404)

This avoids splitting equal cycle coordinates across training and validation. It does not prove independent cells, stationary conditions or future forecast accuracy. The same holdout chooses the family, so its winning score is a selection diagnostic rather than a separate untouched final test. Duplicates within a partition still contribute as repeated observations; there is no grouping by cell or experiment beyond caller selection.

## 4. Bounded EOL and residual bootstrap

For horizon $H=3\max_i n_i$, `eol_cycle` evaluates 100000 equally spaced points in $[0, H]$ and returns the first where $\hat q(n)\le fQ_0$. Otherwise it returns `None`. With $H>0$, grid spacing is $H/99{,}999$. For a continuous monotone curve whose crossing is in-range, the grid result is at or just after that root, up to one grid spacing apart subject to floating-point behavior. The threshold is relative to the **fitted** $Q_0$, not necessarily the first recorded capacity. `project` has neither this horizon restriction nor a capacity clamp. [bcla/core.py:70–111](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L70-L111)

The bootstrap centers residuals, resamples them independently with replacement at the original cycle coordinates, forms synthetic responses $y_i^*=\hat q(n_i)+r_i^*$, and refits the **same selected family**. It requires more observations and distinct cycles than fitted parameters plus positive residual variation. Refit failures are counted separately from replicates with no in-window EOL. Every requested replicate must be successful before percentile bounds are returned. [bcla/core.py:407–533](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L407-L533)

With confidence $c$, successful bounds use empirical quantiles $(1-c)/2$ and $1-(1-c)/2$. RUL is $\max(0, n_f-n_{\mathrm{current}})$ for the point estimate and each replicate. The default current coordinate is the largest observed cycle. These intervals condition on the selected model and the resampling assumptions; they do not include model-family selection, protocol uncertainty, calibration error, measurement uncertainty not represented by residuals, or serial/heteroscedastic residual structure. Censored or failed replicates must not be silently dropped to manufacture finite bounds. [bcla/core.py:435–533](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L435-L533)

## 5. Current throughput and Oxford preprocessing

For measured samples $t_i$ in seconds and current $I_i$ in amperes, define $I_i^+=\max(I_i, 0)$. The implemented interval increment is

$$\Delta\mathrm{EFC}_i=\frac{(I_i^++I_{i+1}^+)(t_{i+1}-t_i)}{2\cdot3600\cdot Q_{\mathrm{nom, Ah}}}.$$

EFC begins at zero at the first measurement. For query offset $u\in[0,\Delta t_i]$, the partial interval uses the integral of the linearly interpolated **clipped samples**:

$$\Delta\mathrm{EFC}(u)=\frac{I_i^+u+(I_{i+1}^+-I_i^+)u^2/(2\Delta t_i)}{3600Q_{\mathrm{nom, Ah}}}.$$

This defines an interpolation convention; it is not generally equal to clipping a linearly interpolated signed-current trace. Only discharge throughput is counted. Seconds/Ah units and current sign must be supplied consistently. [bcla/datasets.py:108–203](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L108-L203)

The Oxford text adapter stably sorts profile time, averages duplicate-time currents and records affected counts. Fully nonfinite trailing profile rows can be removed; partially nonfinite or interior invalid rows are rejected. Capacity check times must be strictly increasing with positive finite capacities. A single final capacity check beyond the current profile can be capped only when the gap is ≤1800 s and final absolute current ≤1 mA. First-check capacity provides the normalization reference; nominal 16 Ah sets the EFC denominator. These repairs and conventions are separate from the empirical fitter. [examples/oxford_energy_trading.py:25–54](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L25-L54) [examples/oxford_energy_trading.py:123–247](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L123-L247)

## 6. Temperature helper and browser proxy

The native helper returns

$$AF=\exp\left[\frac{E_a}{k_B}\left(\frac{1}{T_{\rm ref, K}}-\frac{1}{T_K}\right)\right],\qquad
k_B=8.617333262\times10^{-5}\ \mathrm{eV/K},\quad T_K=T_C+273.15.$$

Default $T_{\rm ref}=25^\circ$C and $E_a=.5$ eV. It rejects nonfinite values and temperatures at/below absolute zero, and requires a finite positive result. Negative activation energy is allowed; the usual increasing-temperature acceleration interpretation assumes $E_a>0$. Native fitted curves do not call this helper. The temperature plot explicitly scales an illustrative linear rate by $AF$, independently of fitting. [bcla/core.py:539–566](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L539-L566) [bcla/viz.py:153–201](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/viz.py#L153-L201)

The browser instead uses $k_b=(f_b/100000)\exp((T_C-25)/20)\sqrt{C_r}$ and $s(n)=\exp(-k_bn)$ over a fixed 1000-cycle window. Its metrics are retention $100 s$, capacity $Q_{0, Ah}s$, resistance-growth proxy $200(1-s)$, and throughput $3.7Q_{0, Ah}(1-s)/(1000k_b)$ kWh. The last expression is the analytic integral of remaining capacity under the page's 3.7 V assumption. It does not solve an EOL threshold or fit observations. The base coefficient 18 does not mean exactly 18% loss at 1000 cycles: at default temperature/rate it gives about 83.527% retention. [docs/index.html:183–189](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L183-L189) [docs/index.html:269–273](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L269-L273)
