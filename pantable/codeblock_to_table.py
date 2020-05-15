import panflute

from .csv_to_table_ast import csv_to_table_ast
from .csv_to_table_markdown import csv_to_table_markdown
from .util import EmptyTableError


def codeblock_to_table(options, data, **args):
    use_pipe_tables = options.get('pipe_tables', False)
    use_grid_tables = options.get('grid_tables', False)

    try:
        if use_pipe_tables or use_grid_tables:
            # if both are specified, use grid_tables
            return csv_to_table_markdown(options, data, use_grid_tables)
        else:
            return csv_to_table_ast(options, data)

    # delete element if table is empty (by returning [])
    # element unchanged if include is invalid (by returning None)
    except FileNotFoundError:
        panflute.debug("pantable: include path not found. Codeblock shown as is.")
        return
    except EmptyTableError:
        panflute.debug("pantable: table is empty. Deleted.")
        # [] means delete the current element
        return []
    except ImportError:
        return
