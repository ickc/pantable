import csv
import io

import panflute

from .const import LETTER_TO_ALIGN
from .util import EmptyTableError


def read_csv(include, data, encoding=None, csv_kwargs={}):
    """Parse CSV table.

    `include`: path to CSV file or None. This is prioritized first.

    `data`: str of CSV table.

    Return None when the include path is invalid.
    """
    with (io.StringIO(data) if include is None else io.open(str(include), encoding=encoding)) as f:
        table_list = list(csv.reader(f, **csv_kwargs))

    if not table_list:
        raise EmptyTableError

    return table_list


def regularize_table_list(raw_table_list):
    """When the length of rows are uneven, make it as long as the longest row.

    `raw_table_list` modified inplace.

    return `n_col`
    """
    length_of_rows = [len(row) for row in raw_table_list]
    n_col = max(length_of_rows)

    for i, (n, row) in enumerate(zip(length_of_rows, raw_table_list)):
        if n != n_col:
            row += [''] * (n_col - n)
            panflute.debug(f"pantable: the {i}-th row is shorter than the longest row. Empty cells appended.")
    return n_col


def parse_alignment(alignment_string, n_col):
    """
    `alignment` string is parsed into pandoc format (AlignDefault, etc.).
    Cases are checked:

    - if not given, return None (let panflute handle it)
    - if wrong type
    - if too long
    - if invalid characters are given
    - if too short
    """

    def get(key):
        '''parsing alignment'''
        key_lower = key.lower()
        if key_lower not in LETTER_TO_ALIGN:
            panflute.debug(f"pantable: alignment: invalid character {key} found, replaced by the default 'd'.")
            key_lower = 'd'
        return LETTER_TO_ALIGN[key_lower]

    # alignment string can be None or empty; return None: set to default by
    # panflute
    if not alignment_string:
        return

    # test valid type
    if not isinstance(alignment_string, str):
        panflute.debug("pantable: alignment should be a string. Set to default instead.")
        # return None: set to default by panflute
        return

    n = len(alignment_string)

    if n > n_col:
        alignment_string = alignment_string[:n_col]
        panflute.debug("pantable: alignment string is too long, truncated.")

    alignment = [get(key) for key in alignment_string]

    # fill up with default if too short
    if n < n_col:
        alignment += ["AlignDefault"] * (n_col - n)

    return alignment
