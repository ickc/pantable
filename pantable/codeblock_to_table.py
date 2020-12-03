from __future__ import annotations

from typing import TYPE_CHECKING
import sys

from .ast import PanCodeBlock
from .util import EmptyTableError

if TYPE_CHECKING:
    from typing import Optional

    from panflute.elements import Doc, CodeBlock

def codeblock_to_table(
    options: Optional[dict] = None,
    data: str = '',
    element: Optional[CodeBlock] = None,
    doc: Optional[Doc] = None,
):
    try:
        return (
            PanCodeBlock
            .from_yaml_filter(options=options, data=data, element=element, doc=doc)
            .to_pantablestr()
            .to_pantable()
            .to_panflute_ast()
        )
    # delete element if table is empty (by returning [])
    # element unchanged if include is invalid (by returning None)
    except FileNotFoundError:
        print("pantable: include path not found. Codeblock shown as is.", file=sys.stderr)
        return
    except EmptyTableError:
        print("pantable: table is empty. Deleted.", file=sys.stderr)
        # [] means delete the current element
        return []
    except ImportError:
        return
