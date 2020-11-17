import panflute

from ..table_to_csv import table_to_csv


def main(doc: panflute.Doc = None):
    """Covert all tables to CSV table format defined in pantable

    - in code-block with class table
    - metadata in YAML
    - table in CSV
    """
    return panflute.run_filter(
        table_to_csv,
        doc=doc
    )


if __name__ == '__main__':
    main()
