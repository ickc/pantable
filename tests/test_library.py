"""pantable as a library: its own representations, in process.

Unlike the rest of the suite, these tests use pantable's API to the AST
library it is built on (panflute), so they change with it.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from panflute import convert_text

from pantable.ast import PanCodeBlock, PanTable
from pantable.util import convert_texts, convert_texts_fast, eq_panflute_elems, parse_markdown_codeblock

from .conftest import GOLDEN


def to_markdown(elem) -> str:
    return convert_text(elem, input_format="panflute", output_format="markdown")


def to_native(elem) -> str:
    return convert_text(elem, input_format="panflute", output_format="native")


def read_table(path: Path):
    doc = convert_text(path.read_text(), input_format="native")
    # each file holds a single table
    assert len(doc) == 1
    return doc[0]


NATIVE = sorted((GOLDEN / "pantable2csvx").glob("*.native"))
CODEBLOCKS = sorted((GOLDEN / "pantable").glob("*.md"))


def codeblock_round_trip(text: str) -> str:
    kwargs = parse_markdown_codeblock(text)
    return to_markdown(PanCodeBlock.from_yaml_filter(**kwargs).to_panflute_ast())


@pytest.mark.parametrize("path", CODEBLOCKS, ids=lambda p: p.stem)
def test_codeblock_idempotent(path: Path) -> None:
    """PanCodeBlock writes a code block that it reads back into the same code block."""
    once = codeblock_round_trip(path.read_text())
    assert once.strip() == codeblock_round_trip(once).strip()


@pytest.mark.parametrize("path", NATIVE, ids=lambda p: p.stem)
def test_table_identity(path: Path) -> None:
    """Table -> PanTable -> ... -> Table, through each of pantable's representations."""
    table = read_table(path)
    pan_table = PanTable.from_panflute_ast(table)
    # PanTableMarkdown
    pan_table_markdown = pan_table.to_pantablemarkdown()
    # PanCodeBlock
    pan_codeblock = pan_table_markdown.to_pancodeblock(fancy_table=True)
    tables = (
        pan_table.to_panflute_ast(),
        pan_table_markdown.to_pantable().to_panflute_ast(),
        pan_codeblock.to_pantablestr().to_pantable().to_panflute_ast(),
    )
    native = to_native(table)
    for table_idem in tables:
        assert to_native(table_idem) == native


@pytest.mark.parametrize("path", NATIVE, ids=lambda p: p.stem)
def test_pantablestr(path: Path) -> None:
    """PanTableStr, without markdown, is lossy: check that it runs."""
    pan_table_str = PanTable.from_panflute_ast(read_table(path)).to_pantablestr()
    pan_table_str.to_pancodeblock()
    pan_table_str.to_pantable()


TEXTS_1 = ["some **markdown** here", "and ~~some~~ other?"]
TEXTS_2 = [
    "some *very* intersting markdown [example]{#so_fancy}",
    """# Comical

Text

# Totally comical

Text""",
]
TEXTSS = [TEXTS_1, TEXTS_2, TEXTS_1 + TEXTS_2]


@pytest.mark.parametrize("texts", TEXTSS)
def test_convert_texts_markdown_to_panflute(texts: list[str]) -> None:
    assert eq_panflute_elems(convert_texts(texts), convert_texts_fast(texts))


@pytest.mark.parametrize("texts", TEXTSS)
def test_convert_texts_panflute_to_markdown(texts: list[str]) -> None:
    elems = convert_texts(texts)
    assert texts == convert_texts_fast(elems, input_format="panflute", output_format="markdown")
