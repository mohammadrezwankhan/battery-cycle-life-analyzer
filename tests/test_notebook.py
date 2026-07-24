"""Notebook smoke checks for the demo artifact."""

import json
from pathlib import Path
import ast


def _demo_notebook_path() -> Path:
    return Path("notebooks") / "demo.ipynb"


def test_notebook_is_valid_json():
    path = _demo_notebook_path()
    raw = path.read_text(encoding="utf-8")
    payload = json.loads(raw)

    assert payload["nbformat"] == 4
    assert payload["nbformat_minor"] >= 4
    assert "cells" in payload


def test_notebook_cells_compile_and_no_obsolete_install_instruction():
    path = _demo_notebook_path()
    payload = json.loads(path.read_text(encoding="utf-8"))

    code_cells = [
        "".join(cell["source"]) for cell in payload["cells"]
        if cell.get("cell_type") == "code"
    ]

    full_source = "\n".join(code_cells)
    assert "pip install -e ." not in full_source

    for source in code_cells:
        ast.parse(source)


def test_notebook_mentions_colab_bootstrap_and_demo_constraints():
    path = _demo_notebook_path()
    payload = json.loads(path.read_text(encoding="utf-8"))

    all_cells = ["\n".join(cell["source"]) for cell in payload["cells"]]
    text = "\n".join(all_cells)

    assert "pip install --upgrade pip" in text
    assert "git+https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer.git" in text
    assert "Projected EOL (80%)" in text
    assert "Projected RUL (80%)" in text
    assert "if eol is None" in text
