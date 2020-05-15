import panflute

from ..pantable import convert2table


def main(doc=None):
    """
    Fenced code block with class table will be parsed using
    panflute.yaml_filter with the fuction convert2table above.
    """
    return panflute.run_filter(
        panflute.yaml_filter,
        tag='table',
        function=convert2table,
        strict_yaml=True,
        doc=doc
    )


if __name__ == '__main__':
    main()
