import panflute
from ..pantable2csv import table2csv


def main(doc=None):
    """
    Any native pandoc tables will be converted into the CSV table format used by pantable:

    - in code-block with class table
    - metadata in YAML
    - table in CSV
    """
    return panflute.run_filter(
        table2csv,
        doc=doc
    )


if __name__ == '__main__':
    main()
