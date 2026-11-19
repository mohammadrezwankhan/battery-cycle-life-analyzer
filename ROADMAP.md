# Twelve-calendar-month development roadmap

**Proposed window: 2026-11-19 through 2027-11-18 inclusive** (end-exclusive 2027-11-19). Dates, effort and role assignments are planning estimates, not funded or staffed commitments. This documentation package implements none of the application, workflow, dependency or scientific changes below.

Now covers 2026-11-19–12-31; Next covers 2027 Q1; Later covers 2027 Q2; Horizon covers 2027-07-01–11-18. Effort is focused person-days, not elapsed delivery time. Each item retains evidence, dependency, uncertainty and verification requirements.

## Now

### BCLA-01 — One unambiguous identity for installed code and release records.

**Correctness / release integrity · P1 · Proposed 2026-11-19–2026-12-31.**

Reconcile pyproject, runtime version and changelog with the existing tag/distribution provenance; add a packaging identity check through a separate release PR.

**Evidence:** [pyproject.toml:5–10](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L5-L10) [bcla/__init__.py:15–15](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/__init__.py#L15-L15) [CHANGELOG.md:5–17](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/CHANGELOG.md#L5-L17) [.github/workflows/publish-pypi.yml:55–78](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/publish-pypi.yml#L55-L78)

**Owner role:** Release maintainer with independent reviewer. **Dependencies:** None. **Effort:** 1–3 person-days. **Confidence:** High.

**Risks:** Changing a public version field or release narrative can misidentify historical distributions. **Unresolved assumptions:** Owner chooses the intended next release and compatibility policy; existing tags remain intact.

**Acceptance criteria:**

- Installed distribution metadata and runtime version agree for a newly tested release candidate.
- Changelog distinguishes already published artifacts from future changes and cites the publishing source/run.

**Verification:** Build and install the candidate wheel outside its checkout; inspect version fields and provenance; run existing package gates.

### BCLA-02 — Explicit preprocessing and time/throughput conventions.

**Correctness / data contracts · P1 · Proposed 2026-11-19–2026-12-31.**

Design backward-compatible normalization-reference and EFC interpolation contracts; evaluate timezone, interval overlap and metadata consistency validation with fixtures before changing defaults.

**Evidence:** [bcla/datasets.py:108–203](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L108-L203) [bcla/datasets.py:352–576](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L352-L576) [bcla/datasets.py:653–923](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L653-L923)

**Owner role:** Data-interface maintainer and scientific reviewer. **Dependencies:** None. **Effort:** 4–7 person-days. **Confidence:** Medium.

**Risks:** Changing normalization or zero-crossing integration silently changes existing numerical results. **Unresolved assumptions:** Expected input time basis and compatibility requirements can be agreed by users.

**Acceptance criteria:**

- Examples cover unsorted normalization, duplicate/aware/naive timestamps, interval overlap and signed-current zero crossings.
- Any proposed alternate convention is explicit and legacy behavior has a migration decision.

**Verification:** Review numerical fixtures against independent hand calculations; run loader/EFC/domain tests and document compatibility results.

### BCLA-03 — All canonical documentation receives repeatable local and hosted coverage.

**Maintainability / documentation verification · P1 · Proposed 2026-11-19–2026-12-31.**

Propose an ordinary CI change for nested Markdown/CFF links, source locator/decorator checks and deterministic handbook freshness while retaining existing jobs and CSP gates.

**Evidence:** [.github/workflows/markdown-maintenance.yml:39–45](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/markdown-maintenance.yml#L39-L45) [.github/workflows/deploy-dashboard.yml:79–90](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/deploy-dashboard.yml#L79-L90) [scripts/browser-csp.mjs:247–286](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/scripts/browser-csp.mjs#L247-L286)

**Owner role:** Documentation maintainer with CI reviewer. **Dependencies:** None. **Effort:** 2–4 person-days. **Confidence:** High.

**Risks:** Unpinned renderer behavior or broad network link checks may be flaky or expensive. **Unresolved assumptions:** A supported pinned rendering environment and network-link policy can be selected.

**Acceptance criteria:**

- An intentionally broken nested link and stale generated guide each fail a focused check.
- Existing required contexts, matrices, release/tag coverage and CSP remain intact.

**Verification:** Exercise positive/negative docs fixtures and observe a candidate-head Actions run before merging.


## Next

### BCLA-04 — A measured-data study can be replayed from explicitly identified inputs.

**Reproducibility / measured-data provenance · P1 · Proposed 2027-01-01–2027-03-31.**

Add an owner-approved Oxford input receipt/cache design with raw digests, archive/license metadata and canonicalization counts; define offline replay separately from opt-in live availability checks.

**Evidence:** [examples/oxford_energy_trading.py:25–108](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L25-L108) [examples/oxford_energy_trading.py:123–257](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L123-L257) [docs/oxford-energy-trading.md:83–112](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/oxford-energy-trading.md#L83-L112) [tests/test_oxford_live.py:1–48](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/tests/test_oxford_live.py#L1-L48)

**Owner role:** Data steward and scientific reviewer. **Dependencies:** BCLA-02. **Effort:** 4–8 person-days. **Confidence:** Medium.

**Risks:** Archive access or licensing/redistribution constraints may limit replayable materials. **Unresolved assumptions:** Permitted retention/redistribution and source stability are confirmed before mirroring.

**Acceptance criteria:**

- Every reported result identifies raw inputs, source version, preprocessing policy and EFC denominator.
- Offline replay and live-fetch status have separate, reproducible pass/failure records.

**Verification:** Reproduce a selected cell from authorized frozen inputs in a clean environment and compare transformations/metrics with tolerances.

### BCLA-05 — Evaluate uncertainty and selection beyond one conditional residual bootstrap.

**Scientific validity / uncertainty · P1 · Proposed 2027-01-01–2027-03-31.**

Design grouped/rolling validation, residual-dependence diagnostics and model-selection uncertainty studies; compare explicit EOL horizon/root policies while preserving unavailable/censored outcomes.

**Evidence:** [bcla/core.py:70–111](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L70-L111) [bcla/core.py:277–404](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L277-L404) [bcla/core.py:407–533](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L407-L533)

**Owner role:** Statistical/scientific reviewer. **Dependencies:** BCLA-02, BCLA-04. **Effort:** 8–15 person-days. **Confidence:** Medium.

**Risks:** Sparse capacity checks and nonstationarity may not support precise intervals or model comparisons. **Unresolved assumptions:** There are enough independent cells/protocols and observations to identify the proposed validation design.

**Acceptance criteria:**

- Study separates selection holdout from untouched evaluation and reports sample/group counts.
- Coverage/censor/failure behavior is measured on known synthetic scenarios and suitable independent data; null results remain reportable.

**Verification:** Review a preregistered analysis protocol, independent implementations/fixtures where feasible, and out-of-sample error/interval coverage summaries.

### BCLA-06 — Existing learning routes expose the current native-source guide without provenance ambiguity.

**Usability / source provenance · P2 · Proposed 2027-01-01–2027-03-31.**

Design a reproducible native-catalog/portfolio refresh with clear historic versus current revisions and explicit separation of browser proxy parameters from native fits.

**Evidence:** [docs/native-lessons.json:8–20](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/native-lessons.json#L8-L20) [docs/portfolio/lesson-config.json:16–18](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/portfolio/lesson-config.json#L16-L18) [docs/index.html:183–189](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L183-L189) [docs/index.html:469–491](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L469-L491)

**Owner role:** Documentation/presentation maintainer. **Dependencies:** BCLA-03. **Effort:** 3–6 person-days. **Confidence:** High.

**Risks:** Rewriting embedded configuration can invalidate CSP hashes or personal-note storage keys. **Unresolved assumptions:** A versioned migration policy preserves existing links and learning records.

**Acceptance criteria:**

- Generated catalog links bind to their declared source revision and retain historical context.
- Keyboard, reduced-motion, export and small-screen behavior are reviewed through an actual browser.

**Verification:** Regenerate deterministically, run existing guide/CSP checks, compare old/new state contracts and perform independent browser checks.


## Later

### BCLA-07 — Measured reproducibility and CI cost data support future toolchain decisions.

**Maintainability / CI economics · P2 · Proposed 2027-04-01–2027-06-30.**

Record a scientific environment matrix and successful provider-run timing baselines, then evaluate dependency bounds, caching and duplicate-event opportunities without dropping validation.

**Evidence:** [pyproject.toml:13–17](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L13-L17) [pyproject.toml:60–86](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L60-L86) [.github/workflows/tests.yml:16–65](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/tests.yml#L16-L65) [.github/workflows/hardened-ci.yml:19–112](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/hardened-ci.yml#L19-L112) [AGENTS.md:1–3](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/AGENTS.md#L1-L3)

**Owner role:** Maintainer and CI owner. **Dependencies:** BCLA-01, BCLA-03. **Effort:** 4–8 person-days. **Confidence:** Medium.

**Risks:** Native scanner builds, network data and runner changes can dominate timings; tighter bounds can exclude supported users. **Unresolved assumptions:** Actions usage and comparable successful-run telemetry are available.

**Acceptance criteria:**

- A recorded baseline names run, job, source, duration and cap before any timeout proposal.
- Any claimed savings use before/after measured usage and preserve required contexts, matrices, scans, tag coverage and environments.

**Verification:** Re-run comparable revisions/environments, report variation and retained gate coverage, and review any separate workflow/lock change.

### BCLA-08 — A second authorized maintainer can recover code, evidence and delivery.

**Governance / recovery · P2 · Proposed 2027-04-01–2027-06-30.**

Assign backup ownership, document restricted access/recovery custody and rehearse a clean-environment restoration with source/distribution/Pages identities kept separate.

**Evidence:** [CITATION.cff:5–10](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/CITATION.cff#L5-L10) [.github/workflows/publish-pypi.yml:87–109](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/publish-pypi.yml#L87-L109) [.github/workflows/deploy-dashboard.yml:61–90](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/deploy-dashboard.yml#L61-L90)

**Owner role:** Repository owner and designated backup maintainer. **Dependencies:** BCLA-01, BCLA-03, BCLA-04. **Effort:** 2–5 person-days. **Confidence:** Medium.

**Risks:** Account, environment or data access may remain concentrated with one owner. **Unresolved assumptions:** A backup maintainer accepts the role and authorized recovery paths are available.

**Acceptance criteria:**

- A second person reproduces the chosen source and handbook from retained records.
- The exercise logs failures and recovery time without bypassing protections or exposing secrets.

**Verification:** Independent witnessed recovery drill, gate/deployment identity check and owner approval of residual risks and target recovery time.


## Horizon

### BCLA-09 — Determine what additional physical/operating claims independent evidence can support.

**Exploratory research / validation · P3 · Proposed 2027-07-01–2027-11-18.**

Design a separately versioned measured-cell study across controlled conditions; evaluate whether metadata/thermal exposure or richer models improve prediction with explicit units, baselines and uncertainty.

**Evidence:** [bcla/core.py:18–42](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L18-L42) [bcla/core.py:539–566](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L539-L566) [bcla/datasets.py:746–923](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L746-L923) [docs/index.html:183–189](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L183-L189)

**Owner role:** Scientific owner with independent domain/data reviewers. **Dependencies:** BCLA-04, BCLA-05, BCLA-07, BCLA-08. **Effort:** 10–20 person-days for study design and pilot, not full validation/certification. **Confidence:** Low.

**Risks:** Data scarcity, confounding, protocol shifts and parameter non-identifiability may prevent stronger claims. **Unresolved assumptions:** Lawfully usable independent measured data and qualified domain review become available.

**Acceptance criteria:**

- Protocol states target population, coordinate/units, held-out groups, baselines and uncertainty before fitting.
- Pilot distinguishes synthetic teaching, empirical calibration and independent validation, and publishes limitations or null outcomes.

**Verification:** Independent protocol review and reproducible pilot with fixed input receipts, untouched evaluation data and explicit claim boundaries.
