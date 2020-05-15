import panflute

from ..table_to_csv import table_to_csv


def main(doc=None):
    """
    Any native pandoc tables will be converted into the CSV table format used by pantable:

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
