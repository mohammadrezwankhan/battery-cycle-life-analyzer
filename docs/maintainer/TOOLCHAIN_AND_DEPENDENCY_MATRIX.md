# Toolchain and dependency matrix

| Layer | Declared source contract | Observed review / qualification |
| --- | --- | --- |
| Python runtime | ≥3.9; classifiers3.9–3.12 |3.12.14 locally; hosted matrix is separate evidence |
| Scientific dependencies | NumPy ≥1.21, SciPy ≥1.7, Matplotlib ≥3.5 |2.3.5, 1.17.0, 3.10.8 respectively |
| Build | setuptools≥77.0.3, wheel | No fresh candidate wheel build/install by author |
| Package dev extra | pytest |9.2.0 in external review environment |
| Development group | Ruff 0.17.4, mypy 2.4.1, pytest 9.2.0, pytest-cov 7.1.0, Hypothesis 6.170.14, SciPy stubs 1.17.0.2 | Distinct from `.[dev]`; full quality installation/gates not inferred from pytest alone |
| Browser tools | Node ≥22; lockfile; ESLint 9.39.5, TypeScript 5.9.3, Prettier 3.9.10 and related packages | Node pure-model/CSP checks executed; AST extraction used external TypeScript 5.9.3 |
| Notebook | nbformat 4.5 with Python 3.11 metadata; optional Colab bootstrap | Seven source cells executed under3.12/Agg; no Jupyter frontend/Colab install |
| Documentation reading view | Python standard library and Pandoc command | Pandoc 3.1.11.1 used; renderer adds no application dependency |
| CFF validation | Existing CFF 1.2.0 | Official1.2.0 JSON schema; duplicate-key rejection and functioning URI/date-time formats |
| CI scanners | Repository-pinned scanner inputs, hashes and source manifests | Operational inventory retained; no fresh full scanner rebuild or vulnerability audit |

[pyproject.toml:1–17](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L1-L17) [pyproject.toml:51–86](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L51-L86) [package.json:1–28](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/package.json#L1-L28) [build_notebook.py:264–279](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/build_notebook.py#L264-L279) [CITATION.cff:1–16](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/CITATION.cff#L1-L16) [.github/security/README.md:1–42](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/security/README.md#L1-L42)

No new Python/npm application dependencies or lockfile changes accompany the handbook. The external review environment inherited scientific libraries and installed the declared pytest/Ruff versions; this is not a fully locked reconstruction of a hosted runner. Record actual resolved versions whenever publishing numerical outputs. CFF parsing used PyYAML's string-scalar mode for this string-valued record with duplicate-key rejection; that validation is not a general YAML 1.2 conformance claim.

The source maintains separate Python/scanner requirements and an npm lock. Dependabot config defines weekly groups, cooldowns and scoped update constraints. Treat those as declarations, not evidence that current dependencies are vulnerability-free. Update manifests/locks together and run the existing quality/security gates; preserve action SHA pinning and version compatibility. [.github/dependabot.yml:1–82](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/dependabot.yml#L1-L82) [AGENTS.md:1–3](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/AGENTS.md#L1-L3)

`make test` runs native tests;`make demo` writes a CLI plot;`make notebook` executes through Jupyter;`make clean` deletes caches/build outputs. Each has different effects and prerequisites. Do not run generation/cleanup as an assumed read-only verification. [Makefile:1–15](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/Makefile#L1-L15)
