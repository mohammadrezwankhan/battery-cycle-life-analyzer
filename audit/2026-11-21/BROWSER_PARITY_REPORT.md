# Browser teaching lab: architecture and parity review

## Four configured lessons

1. Normalize before comparing trajectories.
2. Separate model selection from a visual fit.
3. Stress the extrapolation boundary.
4. Prepare a bounded life-analysis record.

Source: `docs/index.html`, `docs/lesson-config.json`, `docs/lesson-config.schema.json`; deployed public page https://mohammadrezwankhan.github.io/battery-cycle-life-analyzer/ . The page states synthetic teaching model, local calculations, no device control, no backend execution, and explains it is an independently defined educational surrogate. Its exponential fade/temperature/rate response is not equivalent to the native SciPy linear/power/log model-selection engine. The browser fixed model horizon is a *teaching scenario*, not a Python 3×-observed-cycle EOL estimate. Mathematical equivalence should only be asserted for precisely identical defined calculations.

## Verified evidence vs outstanding tests

The published page was retrievable and contains the four-module UI, lesson presets/checkpoints, CSV export, copy/download JSON affordances, and explicit offline teaching model explanations. The checked-in `lesson-config.json` contains the expected four module records and a JSON schema file. Existing repository tests cover browser CSP/tooling, and the hardened quality workflow has dedicated browser modes; they do not substitute for actual keyboard, cross-browser, screen-reader or download inspection. Interactive browser QA was requested independently; update this report only with observable outcomes from a completed browser run.

## Required outstanding checks

- Interact with all four modules, verify presets and checkpoints, slider boundary handling, stable JSON/configuration exports and CSV output.
- Use multiple engines for compatibility, keyboard controls and screen-reader testing. Confirm no unintended network transmission beyond resource loading.
- A single-browser observation is not a cross-browser pass; a successful learning-lab action does not demonstrate statistical validity of a battery prediction.

**Status at report creation: browser-source review completed; comprehensive interactive and accessibility parity NOT VERIFIED.**
