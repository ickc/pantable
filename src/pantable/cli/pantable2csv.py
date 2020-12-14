import panflute

from ..table_to_codeblock import table_to_codeblock


def main(doc: panflute.Doc = None):
    """Covert all tables to CSV table format defined in pantable

    - in code-block with class table
    - metadata in YAML
    - table in CSV
    """
    return panflute.run_filter(
        table_to_codeblock,
        doc=doc
    )


if __name__ == '__main__':
    main()
