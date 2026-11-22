# Executive summary — scientific hardening audit (2026-11-21)

The [22 November verification update](FOLLOWUP_VERIFICATION.md) records the six source rechecks, browser results and current release decision. The observations below describe the earlier 21 November candidate.

## Scope and identity

- Repository: https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer ; base branch main at `fe5bb6fca3345f8fa03a025a787bc2e3f9ca2c7d`.
- Controlled branch: `audit/bcla-v030-scientific-hardening`; draft PR https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/pull/71 . No merge, forced update, release publish or Pages deployment was performed.
- Eight workstreams assessed: numerical solver, chronological validation, uncertainty and thermal handling, schema, Oxford EFC, browser teaching lab, CLI/plotting, and release CI.
- The uploaded plan calls for Gemini/Antigravity multi-agent specialists. No native swarm was available here. Source review and GitHub CI were performed without pretending that independent human reviewers approved the implementation.

## Baseline, reproduction and repairs

- Baseline: GitHub Actions 44869544391 (Python 3.9 through 3.12 green; Python 3.12: 190 passed, six Oxford external-data skips, 13 subtests). Historical 94/6 reference is outdated.
- Red-phase regression run 44944259925: 191 passed, **10 intentional regression failures**, six skipped, 13 subtests (Python 3.12); all 10 reproduced across the support matrix. The other tests continued to pass.
- First integrated correction run 44944454660: 201 passed, six skipped, 13 subtests (Python 3.12), with successful Python 3.9–3.12 jobs.
- Implemented: bounded continuous EOL root solving, numerically stable logarithm, explicit capacity unit contract, dimensional and identifiability guards, finite parameter/covariance checks, negative-data rejection, actionable CLI errors, and atomic figure writes. This branch also aligns the runtime version and adds analytic, leakage and overwrite tests; **the final documentation/metadata commit requires new CI verification**.
- Candidate build and installed-wheel smoke passed: 44944454661. Candidate CodeQL passed: 44944454689. Broader hardened CI was still pending at report authoring.

## Scientific caveats and decision

The empirical three-family fit is **not** a mechanistic electrochemical reliability model. The residual bootstrap does not cover serially dependent/heteroscedastic errors, model-form uncertainty or extrapolation beyond its three-times-observed limit. Six Oxford live-data cases did not execute to numerical completion; no measured-data claim is made. The web lab is a separate deterministic teaching proxy rather than SciPy parity. Supported-browser interaction and accessibility testing remain separately scoped.

**Release recommendation: NO-GO pending the unresolved verification gates.** This report is a reproducible audit snapshot, not an approval to publish v0.3.1 or merge PR #71.

## Subsequent CI and browser evidence

- After the next batch of analytic EOL, future-knee, runtime-version and overwrite tests, commit `0c79e9a8c1793efb993a472c47094d65f9da3d9e` passed the Python 3.9–3.12 matrix: **207 passed, 6 skipped** on Python 3.12 (Actions run 44945020384); candidate wheel, CodeQL and documentation workflows also passed.
- Full Hardened CI run 44945020410 completed with 11 successful jobs and **one failing Python lint job**. Python coverage gate *passed* after the additional tests; the lint report lists only five style violations from `os.replace` and unused mock arguments. Both are corrected in the next branch commit without weakening any lint or coverage threshold. Its final run must still be observed.
- A live read-only Chromium QA run https://agent.tinyfish.ai/runs/44e091f0-3488-4e71-835f-71c7d71800ad successfully exercised all four browser learning modules, presets/checkpoints, metric tabs, simulation start/pause/reset, a synthetic CSV export (241 samples), and lesson-config JSON copy/download. The page explained the 1,000-cycle *teaching* horizon and separation from native SciPy fitting. Keyboard, screen-reader, JSON schema and non-Chromium checks were not performed.

## Champion-quality second-pass results and scope (2026-11-21)

Independent examination of the first audit package found six additional defects spanning nine regression cases. The [pre-fix red suite](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44958435880) failed eight original adversarial tests in Python 3.9–3.12. After code repair (commit `3a5b07fc4bbe49780c89a76a52614162f4cd1502`), [Python matrix 44958616553](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44958616553) passed all four versions: **216 passed, six Oxford live skips, 13 subtests on Python 3.12**. Package validation, CodeQL, secrets/SAST/dependencies/Trivy and Python coverage passed. Hardened CI run 44958616487 nevertheless failed Python lint on a single N802 test-function uppercase-name violation. That function is renamed in the next commit and **must be rechecked on its exact head**. CI rules and coverage thresholds have not been weakened.

Independent calculation from the official Oxford Archive original measured CSVs (same clipped-then-trapezoidal EFC convention) matches historical values for BMP_cell1 (412.367955 EFC, 97.5258235% retention), BMP_cell2 (410.121400 EFC, 97.5584702% retention), SPM_cell1 (689.231401 EFC, 98.3521604% retention), and SPM_cell2 (689.929320 EFC, 98.2332955% retention), all within the recorded tolerances. No raw Oxford files were committed or redistributed. The large BMR_cell1 profile was blocked by the archive and BMR_cell2 was not retrieved. The full six-cell measured-data gate remains **BLOCKED**. See `OXFORD_MEASURED_RECHECK.md`.

An additional read-only keyboard/mobile browser QA attempt failed at the remote test-service layer without providing a usable interaction transcript. Do not represent it as accessibility or cross-browser success. The earlier Chromium click-through remains useful but incomplete.

**No-go for merge/PyPI publication** until complete scientific gate evidence and independent scientific/systems sign-offs. The existing published package is v0.3.0; any follow-up distribution needs its own properly reviewed version and tag. No new release is claimed.

## Third-pass cell-identity validation: cross-cell collision repaired

While reviewing grouping integrity, an independent source inspection found that `_build_history_envelope` formed a compound key by directly concatenating `cell_id + '|' + experiment_id`. The distinct pairs (cell_id `A|B`, experiment_id `C`) and (cell_id `A`, experiment_id `B|C`) therefore both mapped to `A|B|C`, silently mixing separate cell histories. This is a **P1** data-governance defect, not cosmetic formatting. A focused test reproduced its failure on [run 44959344574](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44959344574) (1 envelope instead of 2). `_history_envelope_key` now escapes each identifier component before joining, maintaining legacy keys for ordinary identifiers. After repair, the [Python 3.9–3.12 test matrix 44959498928](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44959498928) succeeded: **217 passed, 6 Oxford live skips, 13 subtests** on Python 3.12. The [Hardened CI run 44959498963](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44959498963), [CodeQL 44959498971](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44959498971), and [candidate wheel 44959499009](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44959499009) also succeeded **on that source commit**. This subsequent evidence-report commit needs its own exact-head verification before merge.

Current total: **18 recorded fixed source/release findings** (P1=9, P2=9), with six Oxford live-data tests and independent scientific/systems review outstanding. GitHub's configured CI passing is not evidence those non-CI gates passed.
