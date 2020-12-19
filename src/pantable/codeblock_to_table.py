from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from .ast import PanCodeBlock
from .util import EmptyTableError

if TYPE_CHECKING:
    from typing import Optional, Union

    from panflute.elements import CodeBlock, Doc
    from panflute.table_elements import Table

logger = getLogger('pantable')


def codeblock_to_table(
    options: Optional[dict] = None,
    data: str = '',
    element: Optional[CodeBlock] = None,
    doc: Optional[Doc] = None,
) -> Union[Table, list, None]:
    try:
        pan_table_str = (
            PanCodeBlock
            .from_yaml_filter(options=options, data=data, element=element, doc=doc)
            .to_pantablestr()
        )
        if pan_table_str.table_width is not None:
            pan_table_str.auto_width()
        return (
            pan_table_str
            .to_pantable()
            .to_panflute_ast()
        )
    # delete element if table is empty (by returning [])
    # element unchanged if include is invalid (by returning None)
    except FileNotFoundError as e:
        logger.error(f'{e} Codeblock shown as is.')
        return None
    except EmptyTableError:
        logger.warning("table is empty. Deleted.")
        # [] means delete the current element
        return []
    except ImportError as e:
        logger.error(f'Some modules cannot be imported, Codeblock shown as is: {e}')
        return None
