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

## Live Chromium functional QA (2026-11-21)

Run evidence: https://agent.tinyfish.ai/runs/44e091f0-3488-4e71-835f-71c7d71800ad (read-only browser automation, no login). All four module tabs changed content; each lesson preset loaded and Check outcomes responded. The tool observed retention 90.484% and remaining capacity 45.242 Ah in the prescribed 50-Ah illustrative case at 1,000 cycles, with the teaching label. Run/Pause/Reset, metric tabs, four parameters, timeline controls, chart and scenario status responded. Export CSV downloaded `battery-cycle-life-analyzer-synthetic-telemetry.csv` with a 241-sample success toast; the configuration modal displayed JSON, Copy JSON changed to Copied, and Download JSON produced `lesson-config.json` with a success toast. The page explicitly distinguished its exponential surrogate, fixed 1,000-cycle teaching horizon and 25°C input from Python regression/holdout/bootstrapping.

**Observed functional outcome: PASS in one Chromium-based run, zero observed UI failures.** The QA did not machine-parse downloaded CSV/JSON files against the schema, execute keyboard traversal or screen-reader testing, or run Firefox/Safari, and therefore makes **no cross-browser/accessibility/schema conformance certification**. The configured browser CI tests passing likewise do not establish those unperformed checks.


## Second independent interaction attempt

A second remote Chromium browser automation run attempted keyboard focus, Escape handling, narrow mobile layout and schema/export inspection on 2026-11-21 but the remote browser service returned an internal failure without usable evidence. Treat these detailed UI and accessibility checks as **UNVERIFIED**; do not infer success from the earlier click-based walk-through. This does not change the educational-proxy/source separation already inspected.