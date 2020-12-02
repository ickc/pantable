from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import csv
import io

import numpy as np

from .util import EmptyTableError

if TYPE_CHECKING:
    from .ast import PanTableOption


def load_csv(
    data: str,
    options: PanTableOption,
    encoding: Optional[str] = None,
):
    include = options.include
    with (io.StringIO(data) if include is None else io.open(str(include), encoding=encoding)) as f:
        table_list = list(csv.reader(f, **options.csv_kwargs))

    if not table_list:
        raise EmptyTableError

    return table_list


def dump_csv(
    data: np.ndarray[str],
    options: PanTableOption,
) -> str:
    # TODO: if options.include...
    with io.StringIO() as file:
        writer = csv.writer(file, **options.csv_kwargs)
        writer.writerows(data)
        return file.getvalue()
