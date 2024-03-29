from __future__ import annotations

from typing import TYPE_CHECKING

from panflute.io import run_filter
from panflute.tools import yaml_filter

from ..codeblock_to_table import codeblock_to_table

if TYPE_CHECKING:
    from panflute.elements import Doc


def main(doc: Doc | None = None):
    """a pandoc filter converting csv table in code block

    Fenced code block with class table will be parsed using
    panflute.yaml_filter with the fuction
    :func:`pantable.codeblock_to_table.codeblock_to_table`
    """
    return run_filter(
        yaml_filter,
        doc=doc,
        tag="table",
        function=codeblock_to_table,
        strict_yaml=True,
    )


if __name__ == "__main__":
    main()
