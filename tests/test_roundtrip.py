"""Round trips between pandoc tables and pantable's code blocks, through the filters."""

from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import GOLDEN, ROOT, pandoc


def cases(filter_: str, suffix: str) -> list[Path]:
    return sorted((GOLDEN / filter_).glob(f"*{suffix}"))


def read(path: Path) -> str:
    return str(path.relative_to(ROOT))


@pytest.mark.parametrize("path", cases("pantable", ".md"), ids=lambda p: p.stem)
def test_back_and_forth(path: Path) -> None:
    """Converting back and forth runs, such as on a table without a body."""
    filters = ("pantable", "pantable2csvx")
    md = pandoc("-t", "markdown", read(path), filters=filters).stdout
    pandoc("-f", "markdown", "-t", "markdown", text=md, filters=filters)


@pytest.mark.parametrize("path", cases("pantable2csvx", ".native"), ids=lambda p: p.stem)
def test_table_lossless(path: Path) -> None:
    """pantable2csvx then pantable gives back the table, as pandoc's native shows it."""
    native = pandoc("-f", "native", "-t", "native", read(path)).stdout
    md = pandoc("-f", "native", "-t", "markdown", read(path), filters=("pantable2csvx",)).stdout
    assert pandoc("-f", "markdown", "-t", "native", text=md, filters=("pantable",)).stdout == native


@pytest.mark.parametrize("path", cases("pantable2csvx", ".native"), ids=lambda p: p.stem)
def test_table_lossy(path: Path) -> None:
    """pantable2csv loses what CSV cannot hold, but what it writes still reads as a table."""
    md = pandoc("-f", "native", "-t", "markdown", read(path), filters=("pantable2csv",)).stdout
    native = pandoc("-f", "markdown", "-t", "native", text=md, filters=("pantable",)).stdout
    assert native.startswith("[ Table")
