from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from .ast import PanCodeBlock
from .util import EmptyTableError

if TYPE_CHECKING:
    from panflute.elements import CodeBlock, Doc
    from panflute.table_elements import Table

logger = getLogger("pantable")

# panclude's attributes beside include, which pantable does not read
PANCLUDE_ONLY = ("startLine", "endLine", "start-line", "end-line", "dedent", "raw")


def include_attribute(element: CodeBlock) -> bool:
    """Append the text of the file named by the code block's ``include`` attribute, as panclude does.

    The file is read as UTF-8, a byte order mark and its final newline dropped, line endings as ``\\n``,
    and goes after the block's own text, on a line of its own. The attribute is then removed.

    Return False if the file cannot be read: the block is then left as it is.
    """
    path = element.attributes["include"]
    if ignored := [key for key in PANCLUDE_ONLY if key in element.attributes]:
        logger.warning(f'include="{path}": {", ".join(ignored)} ignored, run panclude first to use them.')
    try:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read()
    except FileNotFoundError:
        reason = "not found"
    except UnicodeDecodeError:
        reason = "not UTF-8"
    except OSError:
        reason = "cannot be read"
    else:
        if text:
            text = text.removesuffix("\n")
            element.text = f"{element.text}\n{text}" if element.text else text
        del element.attributes["include"]
        return True
    logger.error(f'cannot include "{path}": {reason}. Codeblock shown as is.')
    return False


def codeblock_to_table(
    options: dict | None = None,
    data: str = "",
    element: CodeBlock | None = None,
    doc: Doc | None = None,
) -> Table | list | None:
    try:
        pan_table_str = PanCodeBlock.from_yaml_filter(
            options=options, data=data, element=element, doc=doc
        ).to_pantablestr()
        if pan_table_str.table_width is not None:
            pan_table_str.auto_width()
        return pan_table_str.to_pantable().to_panflute_ast()
    # delete element if table is empty (by returning [])
    # element unchanged if include is invalid (by returning None)
    except FileNotFoundError as e:
        logger.error(f"{e} Codeblock shown as is.")
        return None
    except EmptyTableError:
        logger.warning("table is empty. Deleted.")
        # [] means delete the current element
        return []
    except ImportError as e:
        logger.error(f"Some modules cannot be imported, Codeblock shown as is: {e}")
        return None
