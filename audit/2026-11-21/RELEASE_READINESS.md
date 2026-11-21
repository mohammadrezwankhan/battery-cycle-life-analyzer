# Release readiness: mandatory eight gates

**Overall: AUDIT PARTIALLY COMPLETE — VERIFICATION OUTSTANDING.** This is a *no-publish/no-merge* verdict, not a certification of scientific predictions. Candidate first green Python matrix and package validation are pinned to `a19276ac57e03d869c74cab7f8631acf0cc8f4df`; later audit/metadata changes require new checks.

| Gate | Status | Evidence and limits |
| --- | --- | --- |
| G1 Numerical fitting | PASS | Continuous bounded EOL, stable log, input and nonfinite solver regressions; near-singular covariance conditioning still needs deeper study |
| G2 Chronological validation | PASS | Equal-cycle grouping, training-later split, independent late-knee RMSE, after-selection refit; not independent-cell validation |
| G3 Uncertainty | PASS | 3× cap and censor suppression, fixed-seed and draw accounting under defined residual bootstrap; not unconditional coverage |
| G4 Data governance | PASS | Negative/NaN/Inf rejection, optional None, per-cell envelopes in checked tests; mixed timezones warrant follow-up |
| G5 Real-data workflow | BLOCKED | Six Oxford live cases skipped; offline measured-current fixtures are not field-data validation |
| G6 Browser learning path | PASS | Four lessons, presets, controls and CSV/JSON export tested in Chromium; cross-engine, keyboard and machine schema verification remain outside this limited pass |
| G7 CLI/API/figures | PASS | GitHub CI CLI tests, checked 150-DPI figure path and installed-wheel smoke, atomic output repair |
| G8 CI/release | BLOCKED | First code/packaging/CodeQL green, final hardening and review/signoffs missing at this report's timestamp |

## Independent verifier disclosure

The uploaded mission described two named independent agents. No native Antigravity/Gemini swarm was available; these sign-offs are **NOT VERIFIED**, not fabricated. Independent analytical closed-form references, negative tests, CI job receipts and a remote browser inspection provide useful evidence but are not separate human or formally independent reviewer approvals.

## Outstanding action before release

Confirm final HEAD CI/quality/security/package runs, review all report statements, resolve true Oxford access and reproduce measured-data checks where licensed and available, finish browser UX and accessibility QA, commission two independent scientific/system reviews, and receive explicit owner release authorization. The 0.3.0 package and tag are not to be rewritten for this audit.

## Live browser and CI update

- Chromium run https://agent.tinyfish.ai/runs/44e091f0-3488-4e71-835f-71c7d71800ad observed the four working modules and deterministic teaching scenarios, with both CSV/JSON export actions and no browser failures. The G6 pass is *functional in tested Chromium scope only*; do not infer Firefox/Safari/screen-reader or full JSON Schema validation.
- Post-expanded-test Python matrix at 0c79e9a8… passed 207 tests (+ six Oxford skips); package/CodeQL/docs checks also passed. Hardened CI 44945020410 had exactly one failing job: Python lint (five known Ruff diagnostics). Corrected in a follow-up commit; its outcome must be checked before marking G8 PASS. Core coverage gate passed in this run, unlike an earlier branch revision.
