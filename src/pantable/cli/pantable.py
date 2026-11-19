from __future__ import annotations

from typing import TYPE_CHECKING

from panflute.elements import CodeBlock
from panflute.io import run_filter
from panflute.tools import yaml_filter

from ..codeblock_to_table import codeblock_to_table, include_attribute

if TYPE_CHECKING:
    from panflute.base import Element
    from panflute.elements import Doc


def action(element: Element, doc: Doc):
    """Include the file named by an ``include`` attribute, then read the code block as a table.

    A block whose file cannot be read is left as it is.
    """
    if isinstance(element, CodeBlock) and "table" in element.classes and "include" in element.attributes:
        if not include_attribute(element):
            return None
    return yaml_filter(element, doc, tag="table", function=codeblock_to_table, strict_yaml=True)


def main(doc: Doc | None = None):
    """a pandoc filter converting csv table in code block

    Fenced code block with class table will be parsed using
    panflute.yaml_filter with the fuction
    :func:`pantable.codeblock_to_table.codeblock_to_table`,
    after :func:`pantable.codeblock_to_table.include_attribute`
    if it has an ``include`` attribute.
    """
    return run_filter(action, doc=doc)


if __name__ == "__main__":
    main()
