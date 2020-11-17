import panflute

from ..codeblock_to_table import codeblock_to_table


def main(doc: panflute.Doc = None):
    """a pandoc filter converting csv table in code block

    Fenced code block with class table will be parsed using
    panflute.yaml_filter with the fuction
    :func:`pantable.codeblock_to_table.codeblock_to_table`
    """
    return panflute.run_filter(
        panflute.yaml_filter,
        tag='table',
        function=codeblock_to_table,
        strict_yaml=True,
        doc=doc
    )


if __name__ == '__main__':
    main()
