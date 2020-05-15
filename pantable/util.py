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
