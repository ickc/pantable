"""The documentation's examples, and the README, run without a warning.

The site renders them with pantable from their own directory, where their
include paths are relative to.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import ROOT, pandoc

DOCS = ROOT / "docs"
# README.md is rendered as docs/index.qmd
PAGES = [*sorted((DOCS / "examples").glob("*.md")), ROOT / "README.md"]
CWD = {ROOT / "README.md": DOCS}


@pytest.mark.parametrize("filters", [("pantable",), ("pantable", "pantable2csvx")], ids=["pantable", "back"])
@pytest.mark.parametrize("path", PAGES, ids=lambda p: p.stem)
def test_page(path: Path, filters: tuple[str, ...]) -> None:
    res = pandoc("-t", "markdown", str(path), filters=filters, cwd=CWD.get(path, path.parent))
    assert res.stderr == ""
