# Setup and reproducibility

## Install one explicit revision

For the behavior documented here, use a separate checkout and environment:

```bash
git clone https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer.git
cd battery-cycle-life-analyzer
git checkout 02ed161bded286dad4b3624961430a564715c782
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -m bcla --help
```

The manifest declares Python ≥3.9 and minimum NumPy 1.21, SciPy 1.7 and Matplotlib 3.5. The `[dev]` extra adds pytest; it does not pin a complete scientific environment. The separate development dependency group pins quality tools. Record the interpreter, actual resolved dependencies, platform, source SHA, input digest, selected model, random seed and parameters for a reproducible result. [pyproject.toml:5–17](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L5-L17) [pyproject.toml:51–61](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L51-L61)

The author review used Python **3.12.14**, NumPy **2.3.5**, SciPy **1.17.0**, Matplotlib **3.10.8** and pytest **9.2.0** in an external environment. These are observed review versions, not a new lockfile or proof of the whole supported matrix. Floating-point fits and bootstrap quantiles can vary with solver/library versions. The [verification ledger](../maintainer/VERIFICATION_EVIDENCE_LEDGER.md) records actual execution scope.

## Reproduce local checks

```bash
BCLA_RUN_OXFORD_LIVE=0 MPLBACKEND=Agg python -m pytest -q -ra
node --test tests/browser/csp.test.mjs
python scripts/portfolio/validate_guide.py
node scripts/browser-csp.mjs --check
python docs/reference/build_reference.py --check
```

The native tests use `tests/`; the configured hardened quality suite additionally includes security-helper tests and coverage gates. The commands above do not run every hosted security scanner, every supported Python version, or Oxford live data. The browser tools declare Node ≥22. `BCLA_RUN_OXFORD_LIVE=1` explicitly opts into external Oxford access; ordinary local documentation review leaves it off. [pyproject.toml:81–82](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L81-L82) [.github/security/quality.json:7–21](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/security/quality.json#L7-L21) [package.json:5–13](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/package.json#L5-L13) [tests/test_oxford_live.py:1–48](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/tests/test_oxford_live.py#L1-L48)

## Preserve inputs and outputs

The CLI overwrites `bcla_demo.png` in its working directory. Use an output directory outside the checkout and an absolute CSV path after installing the package. The native API does not itself save analysis records. The notebook writes three PNGs; `build_notebook.py` overwrites the tracked notebook, so regeneration belongs in a deliberate notebook change with a reviewed diff. `make notebook` requires a separately provisioned Jupyter/nbconvert environment; that frontend path was not exercised in this review. [bcla/__main__.py:161–178](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/__main__.py#L161-L178) [build_notebook.py:181–279](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/build_notebook.py#L181-L279) [Makefile:8–15](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/Makefile#L8-L15)

PyPI's recorded 0.3.0 distribution was published from a different commit. Installing a release package is a separate reproduction target from this source checkout; do not infer equivalence from the version string. [Release identity details](../maintainer/CI_CD_AND_RELEASE_PLAYBOOK.md).
