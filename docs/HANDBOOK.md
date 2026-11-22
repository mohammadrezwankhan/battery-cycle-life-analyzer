# Battery cycle-life reference handbook

**Reviewed source:** `02ed161bded286dad4b3624961430a564715c782`. **Documentation snapshot:** 2026-11-19. The [reading view](reference/index.html) is derived from these canonical Markdown files; its date is neither a software release nor a deployment receipt.

The native Python package fits linear, power-law and logarithmic curves to cycle–capacity observations, selects a family using a late-cycle holdout, and offers bounded EOL/RUL estimates with conditional residual-bootstrap intervals. The browser teaching lab evaluates a separate synthetic exponential model. Neither interface establishes calibrated battery lifetime or pack-safety performance. [bcla/core.py:18–42](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L18-L42) [bcla/core.py:299–435](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L299-L435) [docs/index.html:183–189](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L183-L189) [docs/index.html:269–273](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L269-L273)

## Choose a task

| Task | Canonical starting point |
| --- | --- |
| Understand provenance and review limits | [Source evidence](SOURCE_EVIDENCE.md) |
| Follow data through the system | [Architecture](developer/ARCHITECTURE.md) |
| Install the pinned source and reproduce checks | [Setup](developer/SETUP_AND_REPRODUCIBILITY.md) |
| Use an API, command or data format | [Contracts](developer/API_CLI_AND_INTERFACES.md), [native declarations](developer/API_REFERENCE.md) |
| Run a synthetic example or examine the notebook | [Worked examples](developer/WORKED_EXAMPLES_AND_LABS.md) |
| Diagnose a failed fit, unavailable interval or loader error | [Troubleshooting](developer/TROUBLESHOOTING.md) |
| Interpret browser sliders and exports | [Browser model catalog](developer/BROWSER_MODEL_CATALOG.md) |
| Check equations and parameter dimensions | [Equations](math-and-physics/EQUATIONS_AND_DERIVATIONS.md), [symbols](math-and-physics/PARAMETERS_AND_SYMBOLS.md), [limits](math-and-physics/ASSUMPTIONS_AND_LIMITS.md) |
| Assess evidence and maintain gates | [Verification ledger](maintainer/VERIFICATION_EVIDENCE_LEDGER.md), [CI and release](maintainer/CI_CD_AND_RELEASE_PLAYBOOK.md), [toolchain](maintainer/TOOLCHAIN_AND_DEPENDENCY_MATRIX.md) |
| Maintain this handbook | [Documentation runbook](maintainer/DOCS_MAINTENANCE_RUNBOOK.md), [failure modes](maintainer/FAILURE_MODES_AND_TECH_DEBT.md) |
| Recover or hand over ownership | [Governance](owner/GOVERNANCE_AND_SCOPE.md), [recovery](owner/BUS_FACTOR_RECOVERY_RUNBOOK.md), [decision index](owner/ADR/ADR-0000-INDEX.md), [portfolio integration](owner/PORTFOLIO_INTEGRATION.md) |
| Plan subsequent work | [Twelve-month roadmap](../ROADMAP.md) |

## Existing material and project records

The [README](../README.md), [contributor guide](../CONTRIBUTING.md), [Oxford walkthrough](oxford-energy-trading.md), [original Markdown introduction](index.md), [notebook](../notebooks/demo.ipynb), [changelog](../CHANGELOG.md), [citation metadata](../CITATION.cff), [license](../LICENSE) and [security guidance](../SECURITY.md) retain their roles. Historical release notes and the dated Oxford audit remain historical records. This handbook explains the pinned source where metadata or older prose differs.

Existing learning routes remain available: [browser lab](index.html), [native catalog](native-lessons.html), [portfolio learning paths](portfolio/index.html) and [animation archive](animations/index.html). The native catalog and learning-path records contain older source revisions; their labels and scripts are preserved rather than silently presented as newly audited native results. [docs/native-lessons.json:8–20](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/native-lessons.json#L8-L20) [docs/portfolio/lesson-config.json:16–18](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/portfolio/lesson-config.json#L16-L18)
