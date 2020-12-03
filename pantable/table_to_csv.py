from __future__ import annotations

from typing import TYPE_CHECKING

from panflute.elements import Table

if TYPE_CHECKING:
    from typing import Optional

    from panflute.elements import Doc

from .ast import PanTable


def table_to_csv(
    element: Optional[Table] = None,
    doc: Optional[Doc] = None,
):
    """convert Table element and to csv table in code-block with class "table" in panflute AST"""
    if type(element) == Table:
        return (
            PanTable
            .from_panflute_ast(element)
            .to_pantablemarkdown()
            # no options chosen here to match historical behavior
            .to_pancodeblock()
            .to_panflute_ast()
        )
    return None
