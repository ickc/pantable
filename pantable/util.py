import panflute


class EmptyTableError(Exception):
    pass


def ast_to_markdown(ast):
    """convert panflute AST to Markdown"""
    return panflute.convert_text(
        ast,
        input_format='panflute',
        output_format='markdown'
    )


def table_for_pprint(table: panflute.Table):
    '''represent panflute Table in a dict structure for pprint

    >>> pprint(table_for_pprint(table), sort_dicts=False, compact=False, width=-1)

    Note:

    Each HeadRow, BodyRow, FootRow, Cell also has ica not shown here.

    TableBody has RowHeadColumns int
    '''
    return {
        'Table': (table.identifier, table.classes, table.attributes),
        'Caption': (tuple(short_caption) if (short_caption := table.caption.short_caption) else None, tuple(table.caption.content)),
        'specs': table.colspec,
        'TableHead': [list(row.content) for row in table.head.content],
        'TableBody': [list(row.content) for row in table.content[0].content],
        'TableFoot': [list(row.content) for row in table.foot.content],
    }
