from __future__ import annotations

from pathlib import Path

from typing import TYPE_CHECKING
import csv
import io
import sys

import numpy as np

from .util import EmptyTableError

if TYPE_CHECKING:
    from typing import Optional, Iterator

    from .ast import PanTableOption


def load_csv(
    data: str,
    options: PanTableOption,
    encoding: Optional[str] = None,
):
    '''loading CSV table

    Note that this can emit EmptyTableError, FileNotFoundError
    '''
    include = options.include
    with (
        open(include, encoding=encoding, newline='')
    ) if include else (
        io.StringIO(data, newline='')
    ) as f:
        table_list = list(csv.reader(f, **options.csv_kwargs))
    if table_list:
        for row in table_list:
            if row:
                for i in row:
                    if i.strip():
                        return table_list
    raise EmptyTableError


def dump_csv_str(
    data: np.ndarray[str],
    options: PanTableOption,
) -> str:
    '''dump data as CSV string
    '''
    with io.StringIO(newline='') as f:
        writer = csv.writer(f, **options.csv_kwargs)
        writer.writerows(data)
        return f.getvalue()


def dump_csv(
    data: np.ndarray[str],
    options: PanTableOption,
) -> Optional[str]:
    '''dump data as CSV

    it will mutate options.include if it is an invalid write path.
    '''
    _include = options.include

    text = dump_csv_str(data, options)

    if _include:
        try:
            include = Path(_include)
            include.parent.mkdir(parents=True, exist_ok=True)
            with open(include, 'x', newline='') as f:
                f.write(text)
            return None
        except (PermissionError, FileExistsError):
            print(f'Data cannot be written to file {options.include}, Overriding include path to empty...', file=sys.stderr)
            options.include = ''
    return text
