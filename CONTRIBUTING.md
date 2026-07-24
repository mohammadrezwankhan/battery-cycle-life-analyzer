# Contributing

Thank you for helping improve Battery Cycle-Life Analyzer. Focused changes that
make the models easier to inspect, validate, or use with real cycling data are
especially welcome.

## Before you start

- Search existing issues and pull requests before opening a duplicate.
- Open an issue before a large API change or a new degradation-model family.
- Do not include confidential, proprietary, or personally identifiable data.
- Only contribute datasets that you have the right to redistribute, and
  document their source, chemistry, protocol, units, and license.

## Development setup

Fork and clone the repository, then create an isolated environment:

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

Or on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Make a focused change

1. Create a branch from the latest `main`.
2. Keep model equations, bounds, assumptions, and units explicit.
3. Add or update tests for behavioral changes.
4. Update the README or docstrings when the public API or interpretation
   changes.
5. Avoid committing generated figures, build artifacts, or private datasets
   unless they are intentionally part of the documentation.

## Verify the change

Run the complete test suite:

```bash
python -m pytest -v
```

For changes that affect the command-line demo, also run:

```bash
python -m bcla --model all
```

The GitHub Actions workflow repeats the tests on all supported Python versions.

## Pull requests

In the pull-request description, explain:

- the engineering or user problem being addressed;
- the chosen approach and any new assumptions;
- how the result was verified;
- any compatibility, numerical, or data-provenance considerations.

Keep pull requests small enough to review. Maintainers may ask that unrelated
changes be split into separate submissions.

## Reporting problems

For numerical or model-fitting problems, include a minimal reproducible example
with:

- Python and dependency versions;
- the selected model and parameter settings;
- a small non-confidential data sample or synthetic reproducer;
- expected and observed behavior;
- the complete error message, if applicable.

Please do not use the issue tracker for battery-safety decisions. Consult a
qualified battery engineer and the cell manufacturer's documentation for
safety-critical work.
