"""The include attribute: pantable's messages, and the same table as with panclude run first.

The tables themselves are golden cases, tests/golden/pantable/include_*.md.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

import pytest

from .conftest import GOLDEN, filter_path, pandoc

CASES = GOLDEN / "pantable"
# panclude.lua (https://github.com/ickc/panclude), at a fixed commit
PANCLUDE = "https://raw.githubusercontent.com/ickc/panclude/aa6a0d53bbdf1209092733b59efb5220d6e46ff6/panclude.lua"


@pytest.mark.parametrize(
    "attributes,message",
    [
        ('include="xyz/csv_tables.csv"', 'cannot include "xyz/csv_tables.csv": not found. Codeblock shown as is.'),
        ('include="csv_table_gbk.csv"', 'cannot include "csv_table_gbk.csv": not UTF-8. Codeblock shown as is.'),
        ('include="."', 'cannot include ".": cannot be read. Codeblock shown as is.'),
        (
            'include="include_rows.csv" startLine=2 dedent=1',
            'include="include_rows.csv": startLine, dedent ignored, run panclude first to use them.',
        ),
    ],
    ids=["not-found", "not-utf8", "directory", "panclude-only"],
)
def test_message(attributes: str, message: str) -> None:
    """A failure, or panclude's own attributes, are logged, naming the path, never the file's content."""
    res = pandoc("-t", "native", text=f"``` {{.table {attributes}}}\n```\n", filters=("pantable",), cwd=CASES)
    # one line, coloured if coloredlogs is installed
    assert len(res.stderr.splitlines()) == 1
    assert message in res.stderr


@pytest.fixture(scope="module")
def panclude(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("panclude") / "panclude.lua"
    try:
        with urllib.request.urlopen(PANCLUDE, timeout=30) as res:
            path.write_bytes(res.read())
    except OSError as e:
        pytest.skip(f"panclude.lua cannot be fetched: {e}")
    return path


@pytest.mark.parametrize(
    "path", sorted(p for p in CASES.glob("*.md") if 'include="' in p.read_text(encoding="utf-8")), ids=lambda p: p.stem
)
def test_same_as_panclude(path: Path, panclude: Path) -> None:
    """pantable alone builds the table that panclude, then pantable, builds."""
    alone = pandoc("-t", "native", path.name, filters=("pantable",), cwd=path.parent).stdout
    both = pandoc(
        "-t", "native", "-L", str(panclude), f"--filter={filter_path('pantable')}", path.name, cwd=path.parent
    )
    assert both.stdout == alone
