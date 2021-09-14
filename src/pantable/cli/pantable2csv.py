from __future__ import annotations

from typing import TYPE_CHECKING

from panflute.io import run_filter

from ..table_to_codeblock import table_to_codeblock

if TYPE_CHECKING:
    from panflute.elements import Doc

#: Equiv. to the pantable2csv cli, but provided as a Python interface.
FILTER = table_to_codeblock


def main(doc: Doc | None = None):
    """Covert all tables to CSV table format defined in pantable

    - in code-block with class table
    - metadata in YAML
    - table in CSV
    """
    return run_filter(FILTER, doc=doc)


if __name__ == "__main__":
    main()
