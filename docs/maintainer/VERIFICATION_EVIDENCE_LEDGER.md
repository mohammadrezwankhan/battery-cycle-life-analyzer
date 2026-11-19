# Verification evidence ledger

**Source under review:** `02ed161bded286dad4b3624961430a564715c782`, tree `47bb084efe6758920bd59101243400b9be9488a7`. **Review date:** 2026-11-19. Source, local documentation candidate, eventual PR head, merge commit and deployed Pages revision are separate identities. This page reports author evidence; independent QA and provider delivery records must bind their own exact revisions.

## Executed and inspected evidence

| Check | Observed result | What it establishes |
| --- | --- | --- |
| Complete source object inventory | 183 entries: 152 blobs and 31 directories; all payload Git IDs verified | Coverage accounting, not full semantic review of every asset/tool |
| Existing native pytest suite, Python 3.12 | **190 passed, 6 skipped, 13 subtests passed** | Actual local source tests; six Oxford live tests opted out |
| Existing browser CSP test suite | **17 passed** | Policy/parser fixtures and source documents; no GUI interaction |
| Existing portfolio validator | **4 learning paths validated** | Paths, canonical config agreement and selected SVG/structure |
| Native and Oxford `--help` | Passed | Parser/help execution; Oxford help downloads nothing |
| Quickstart API and CLI | Passed; selected linear, 9/3 split, 50 successful bootstrap replicates | Synthetic source fixture and output behavior |
| EFC interpolation example | `[.046875,.0625]` at 450/900 s | Clipped-sample convention for one explicit fixture |
| Exact notebook code cells | **7 executed**, 3 PNGs written externally | Sequential Python cell execution; not Jupyter/Colab/frontend validation |
| Active browser degradation checkpoints | **8 passed** in Node | Exact inline pure evaluator and configured fixtures; no DOM execution |
| Python interface extraction | 36 native public declarations, 48 dataclass fields; 376 total declarations in 36 Python files | Decorator-inclusive static source accounting; internal/tooling declarations remain distinguished |
| JavaScript extraction | 9 parsed units, 65 declarations, 36 event registrations | TypeScript 5.9.3 AST plus scoped controller review; dynamic DOM behavior remains unverified |
| Final documentation package checks | Canonical paths, local links/fragments, CFF, source locators, renderer freshness, static HTML/CSP and authorized diff checked | Documentation consistency on the local candidate; no external-link reachability or publication claim |

Native tests and contracts are source-located in [tests](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/tree/02ed161bded286dad4b3624961430a564715c782/tests). The local command receipt retains the six explicit live skips; a skip is not a passed measured-data check. The native test output also includes an external pytest/AnyIO deprecation warning; it is preserved in the review log. [tests/test_oxford_live.py:1–48](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/tests/test_oxford_live.py#L1-L48) [tests/test_notebook.py:1–50](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/tests/test_notebook.py#L1-L50) [tests/browser/csp.test.mjs:1–232](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/tests/browser/csp.test.mjs#L1-L232)

The initial external example harness referenced `ModelSelection.train_size`, which does not exist. The author corrected the harness to `selection.validation_score.train_size` after checking the source and reran it successfully. This was a verification-harness failure, not an application failure; the initial receipt remains retained. Source model/data/notebook bytes were unchanged. [bcla/core.py:128–153](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L128-L153)

## Provider evidence and unexecuted scope

The read-only [exact-source check-run response](https://api.github.com/repos/mohammadrezwankhan/battery-cycle-life-analyzer/commits/02ed161bded286dad4b3624961430a564715c782/check-runs?per_page=100) contained 35 successful records, including repeated contexts from different runs. Statuses were empty. These are historical source-revision results, not candidate-head CI. Examples include [CodeQL Python](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/43918531827/job/133479174411) and [Python quality tests](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/43903332442/job/133425473914). Complete observed pagination and raw responses are retained in the audit records.

Not executed by the author: live Oxford downloads, a fresh PyPI wheel installation, the full hosted security/coverage pipeline, native OpenGrep rebuild or vulnerability database audit, all supported Python versions, browser rendering/keyboard/screen-reader tests, release publishing, merge or deployed-site verification. Existing historical Oxford and release assertions remain dated source records.

Before integration, inspect the actual PR head and complete applicable protection settings; refresh checks, reviews and expected head immediately before merging. After merge, map Pages' deployment to the merged SHA and inspect the changed handbook route. A green older run, an open PR or a page returning HTTP 200 does not establish those outcomes. [Delivery procedure](CI_CD_AND_RELEASE_PLAYBOOK.md).
