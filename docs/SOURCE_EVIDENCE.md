# Source evidence and coverage boundaries

This handbook analyzes immutable commit **`02ed161bded286dad4b3624961430a564715c782`**, tree **`47bb084efe6758920bd59101243400b9be9488a7`**. The complete canonical tree contains **183 entries: 152 blobs and 31 directories**. All blob payloads were independently matched to their Git object IDs; 151 decode as text and one is a PNG. A file being downloaded, parsed or hashed is not equivalent to a full semantic review.

## Dispositions and methods

The operational inventory assigns **74 entries ANALYZED** and **109 INDEXED_ONLY** with an explicit reason for each path. All 31 directory entries are indexed objects. No source entry is omitted. The following describes the scope of those labels:

| Source group | Review method and limit |
| --- | --- |
|`bcla/*.py`, native examples | Complete native behavior, interfaces, scientific assumptions and error/write paths reviewed; native tests and synthetic examples executed separately |
| Native `tests/` | Test bodies reviewed; 190 native tests passed, 6 live skips, 13 passing subtests; 17 separate Node CSP tests passed |
| Notebook and generator | All 14 notebook cells and generator read; 7 exact code cells executed; source notebook remains unchanged |
| Three CSV fixtures | All rows read and parsed; 12 single-cell, 6 metadata and4 history rows; all synthetic |
|`docs/index.html` | Model specs, evaluators, checkpoint and UI/export controller reviewed; active degradation checkpoints executed; CSS/artwork structurally indexed |
| Catalog/portfolio/waveform controllers | Relevant complete state/search/copy/export/drawing logic reviewed; historical source metadata preserved; no GUI claim |
| Workflows, package configuration, main guides | Actual events, matrices, dependencies, release/publication contracts and meaningful text reviewed |
| Operational security tooling | Static definitions, declared gate contracts and relevant quality configuration inspected; most scanner helper bodies, security test bodies, provenance inventories, locks and native export records remain indexed-only; no exhaustive security audit or vulnerability refresh |
| SVG/CSS/generated asset/catalog records | Structural parse, hashes, references and selected provenance; no exhaustive pixel/animation/assistive-technology review |
| PNG and historical README | Immutable binary/history indexing; preserved, not freshly generated or treated as a new measured result |

The public native catalog includes **36 declarations and 48 dataclass fields**, with decorator-inclusive ranges. A complete Python AST traversal accounts for **376 definitions in 36 files**, including conditional/nested/test/tooling declarations. JavaScript AST extraction covers **9 units, 65 declarations and 36 event registrations**, plus embedded JSON and external script references. This supplemental extraction resolves the initial unavailable TypeScript-parser path; the initial diagnostic is retained, not relabeled. Dynamic DOM behavior and operational scanner internals retain their stated limits. [Native catalog](developer/API_REFERENCE.md) · [browser catalog](developer/BROWSER_MODEL_CATALOG.md).

## Claim anchors

| Claim | Immutable source |
| --- | --- |
| Empirical equations, bounds and parameter order | [bcla/core.py:18–53](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L18-L53) |
| Fitting, validation, bounded EOL and bootstrap | [bcla/core.py:57–533](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L57-L533) |
| Temperature helper and illustrative plotting | [bcla/core.py:539–566](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L539-L566) [bcla/viz.py:153–201](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/viz.py#L153-L201) |
| Loaders, metadata, normalization and EFC convention | [bcla/datasets.py:74–262](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L74-L262) [bcla/datasets.py:445–923](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/datasets.py#L445-L923) |
| Oxford fetch/preprocessing and historical audit | [examples/oxford_energy_trading.py:25–257](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L25-L257) [docs/oxford-energy-trading.md:83–112](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/oxford-energy-trading.md#L83-L112) |
| Browser model separation and exports | [docs/index.html:155–344](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L155-L344) [docs/index.html:469–491](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L469-L491) |
| Packaging and version drift | [pyproject.toml:5–17](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L5-L17) [bcla/__init__.py:15–31](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/__init__.py#L15-L31) [CHANGELOG.md:5–17](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/CHANGELOG.md#L5-L17) |
| Existing publication path | [.github/workflows/deploy-dashboard.yml:61–90](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/deploy-dashboard.yml#L61-L90) |

External technical interpretation uses the [official SciPy 1.17 solver contract](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.curve_fit.html). Release metadata was checked through GitHub and the [primary PyPI record](https://pypi.org/project/battery-cycle-life-analyzer/). The Oxford record returned 403 during this review; source-declared attribution remains explicitly separate from fresh archive retrieval. Exact commands, environment versions, hashes, original failure/skip receipts and candidate identities are retained in the six specialist audit handoffs. The [verification ledger](maintainer/VERIFICATION_EVIDENCE_LEDGER.md) states what was and was not executed.
