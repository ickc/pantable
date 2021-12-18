from __future__ import annotations

from typing import TYPE_CHECKING

from panflute.io import run_filter

from ..table_to_codeblock import table_to_codeblock

if TYPE_CHECKING:
    from panflute.elements import Doc


def main(doc: Doc | None = None):
    """Covert all tables to CSV table format defined in pantable

    - in code-block with class table
    - metadata in YAML
    - table in CSV
    """
    return run_filter(table_to_codeblock, doc=doc, fancy_table=True)


if __name__ == "__main__":
    main()
