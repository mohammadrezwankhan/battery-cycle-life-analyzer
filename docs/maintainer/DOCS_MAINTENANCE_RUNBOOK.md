# Documentation maintenance runbook

## One canonical source

Edit Markdown, the existing CFF where separately authorized, and `docs/reference/chapters.json`. The handbook HTML is a generated snapshot. Do not maintain independent prose in `docs/reference/index.html`. The manifest records the full analyzed source SHA and review date; input hashes embedded in HTML cover chapters, renderer, manifest and CSS. Updating those metadata fields requires an actual source review, not only a date change.

```bash
python docs/reference/build_reference.py
python docs/reference/build_reference.py --check
node scripts/browser-csp.mjs --check
node --test tests/browser/csp.test.mjs
python scripts/portfolio/validate_guide.py
python -m ruff check docs/reference/build_reference.py
git diff --check
```

The renderer requires Pandoc on PATH, uses only Python's standard library, and writes one fixed output file. It rewrites links between included chapters into local anchors, keeps existing docs routes relative, and points repository source files outside `docs/` to immutable GitHub URLs. Source-linked native signatures must include decorators as well as definitions. Check all path and fragment destinations after adding/renaming a heading or chapter.

## Review sequence

1. Start with a pinned source tree and a complete inventory. Identify changed scientific assumptions, API signatures, loaders, CLI behavior, tests, workflow events and existing publication routes.
2. Update the smallest affected canonical pages with exact source line citations. Label inferred limitations, proposals, historic claims and actual executed outcomes separately.
3. Run the affected existing checks. Keep source-only execution receipts tied to their original SHA/time; if a later docs-only candidate reuses them, show that their runtime inputs are unchanged. Regenerate the guide and validate its exact content, links, CSP, unique IDs and chapter anchors.
4. Compare the entire candidate diff. Preserve application/scientific code, workflows, dependencies, results, notebook, license and existing citation content unless a separate change authorizes them.
5. Obtain independent review of the exact candidate tree. After merge, bind deployment identity and inspect the live changed route; retain blockers and skipped work honestly.

## Existing presentation and gate constraints

Keep the orange/cream/purple palette, readable content width, visible focus, skip link, responsive contents navigation, scrollable tables, native MathML and print styles. The reference view has no scripts or network data fetch. Its CSP follows the existing repository policy generator, with the policy meta tag first in `head`; do not weaken or remove it to make a build pass. Existing scripts, inline style hashes and config payloads on the three old surfaces remain unchanged by the navigation additions. [scripts/browser-csp.mjs:1–40](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/scripts/browser-csp.mjs#L1-L40) [scripts/browser-csp.mjs:95–225](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/scripts/browser-csp.mjs#L95-L225)

The source link workflow currently checks only README, CONTRIBUTING and top-level `docs/*.md`. A new nested page is not covered merely because it triggers that workflow. Until a separately reviewed CI change broadens coverage, perform the complete local Markdown/HTML link and source-range check and retain its results. Pages uploads committed files directly, so freshness must be checked before commit. [.github/workflows/markdown-maintenance.yml:39–45](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/markdown-maintenance.yml#L39-L45) [.github/workflows/deploy-dashboard.yml:79–90](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/deploy-dashboard.yml#L79-L90)

The existing Oxford guide and catalog are dated artifacts. Preserve useful historical content and annotate newer facts in the current handbook; avoid silently relabeling an old dataset audit or an old source revision. The notebook generator writes the notebook itself; a docs update must not regenerate it incidentally. [docs/oxford-energy-trading.md:83–112](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/oxford-energy-trading.md#L83-L112) [build_notebook.py:275–279](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/build_notebook.py#L275-L279)
