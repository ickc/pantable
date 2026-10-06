"""Each filter's output, compared with tests/golden/<filter>/expected/.

tests/golden/<filter>/<case>.md (or .native) is read with the filter, and
written as Markdown. Regenerate the expected output with

    pixi run gen-golden
"""

from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import FILTERS, GOLDEN, ROOT, pandoc

FORMATS = {".md": "markdown", ".native": "native"}


def cases(filter_: str) -> list[Path]:
    return sorted(p for p in (GOLDEN / filter_).iterdir() if p.suffix in FORMATS)


CASES = [pytest.param(f, p, id=f"{f}/{p.stem}") for f in FILTERS for p in cases(f)]


@pytest.mark.parametrize("filter_,path", CASES)
def test_golden(filter_: str, path: Path, request: pytest.FixtureRequest) -> None:
    out = pandoc("-f", FORMATS[path.suffix], "-t", "markdown", str(path.relative_to(ROOT)), filters=(filter_,)).stdout
    expected = path.parent / "expected" / f"{path.stem}.md"
    if request.config.getoption("--update-golden"):
        expected.write_text(out)
    assert out == expected.read_text()
