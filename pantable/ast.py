from __future__ import annotations

from typing import Union, List, Tuple, Optional
from itertools import chain
from pprint import pformat

import numpy as np

from panflute.table_elements import Table, TableCell
from panflute.containers import ListContainer
from panflute.tools import stringify

try:
    from dataclasses import dataclass
except ImportError:
    raise ImportError('Using Python 3.6? Please run "pip install dataclasses".')


ALIGN = np.array([
    "AlignDefault",
    "AlignLeft",
    "AlignCenter",
    "AlignRight",
])

# inverse of the above, converting the 5-th char to index
ALIGN_TO_IDX = {
    'D': 0,
    'L': 1,
    'C': 2,
    'R': 3,
}

COLWIDTHDEFAULT = 'ColWidthDefault'


@dataclass
class Ica:
    """a class of identifier, classes, and attributes"""
    identifier: str
    classes: list
    attributes: dict


class FakeRepr():
    '''a mixin for fake repr from to_dict method
    '''

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        '''TODO'''
        return pformat(self.to_dict(), sort_dicts=False, compact=False, width=-1)

    def to_dict(self):
        raise NotImplementedError


class Spec(FakeRepr):
    '''a class of spec of PanTable
    '''

    def __init__(
        self,
        aligns: np.ndarray[np.int8],
        col_widths: np.ndarray[np.float64],
    ):
        self.aligns = aligns
        self.col_widths = col_widths

    def to_dict(self) -> dict:
        return {
            'aligns': self.aligns_text,
            'col_widths': self.col_widths,
        }

    @property
    def size(self) -> int:
        return self.aligns.size

    @property
    def aligns_text(self) -> np.ndarray[np.str_]:
        return ALIGN[self.aligns]

    @classmethod
    def from_panflute_ast(cls, table: Table) -> Spec:
        spec = table.colspec

        n = len(spec)
        aligns = np.empty(n, dtype=np.int8)
        col_widths = np.empty(n, dtype=np.float64)

        try:
            for i, (align, width) in enumerate(spec):
                aligns[i] = ALIGN_TO_IDX[align[5]]
                col_widths[i] = np.nan if width == COLWIDTHDEFAULT else width
        except ValueError:
            raise TypeError(f'pantable: cannot parse table spec {spec}')

        return cls(
            aligns,
            col_widths,
        )


class PanCellPlain():
    '''a class of simple cell within PanTable
    '''
    shape = (1, 1)
    idxs: Optional[Tuple[int, int]] = None

    def __init__(self, content: ListContainer):
        self.content = content

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return repr(self.content)


class PanCellBlock(PanCellPlain):
    '''a class of Block cell within PanTable
    '''
    def __init__(
        self,
        content: ListContainer,
        shape: Tuple[int, int],
        idxs: Tuple[int, int],
    ):
        self.content = content
        self.shape = shape
        self.idxs = idxs

    def __repr__(self) -> str:
        return f'PanCellBlock({repr(self.content)}, {repr(self.shape)}, {repr(self.idxs)})'

    def put_array(self, array, overwrite=False):
        '''put itself inside giving array
        '''
        x, y = self.shape
        idx, idy = self.idxs
        for i in range(idx, idx + x):
            for j in range(idy, idy + y):
                if overwrite or array[i, j] is None:
                    array[i, j] = self
                else:
                    raise ValueError(f"At location {self.idxs} there's not enough empty cells for a block of size {self.shape} in the given array {array}")


class PanTable(FakeRepr):
    '''a representation of panflute Table
    '''

    def __init__(
        self,
        ica_table: Ica,
        short_caption: Union[ListContainer, None], caption: ListContainer,
        spec: Spec,
        shape: List[int],
        ms: np.ndarray[np.int64], ns_head: np.ndarray[np.int64],
        icas_body: np.ndarray[Ica],
        icas_row: np.ndarray[Ica],
        icas: np.ndarray[Ica],
        aligns: np.ndarray[np.int8],
        cells: np.ndarray[ListContainer],
    ):
        self.ica_table = ica_table
        self.short_caption = short_caption
        self.caption = caption
        self.spec = spec
        self.shape = shape
        self.ms = ms
        self.ns_head = ns_head
        self.icas_body = icas_body
        self.icas_row = icas_row
        self.icas = icas
        self.aligns = aligns
        self.cells = cells

    def to_dict(self) -> dict:
        '''TODO'''
        return {
            'ica_table': self.ica_table,
            'short_caption': self.short_caption,
            'caption': self.caption,
            'spec': self.spec.to_dict(),
            'shape': self.shape,
            'ms': self.ms,
            'ns_head': self.ns_head,
            'icas_body': self.icas_body,
            'icas_row': self.icas_row,
            'icas': self.icas,
            'aligns': self.aligns_text,
            'cells': self.cells,
        }

    @property
    def aligns_text(self) -> np.ndarray[np.str_]:
        return ALIGN[self.aligns]

    @classmethod
    def from_panflute_ast(cls, table: Table) -> PanTable:
        ica_table = Ica(
            table.identifier,
            table.classes,
            table.attributes,
        )

        short_caption = table.caption.short_caption
        caption = table.caption.content

        spec = Spec.from_panflute_ast(table)
        n = spec.size

        head = table.head
        bodies = table.content
        foot = table.foot

        n_bodies = len(bodies)
        ns_head = np.empty(n_bodies, dtype=np.int64)
        icas_body = np.empty(n_bodies, dtype='O')
        for i, body in enumerate(bodies):
            ns_head[i] = body.row_head_columns
            icas_body[i] = Ica(body.identifier, body.classes, body.attributes)

        # there are 1 head,
        # then n bodies, for each body one head and one content,
        # then 1 foot
        ms = np.empty(2 * len(bodies) + 2, dtype=np.int64)
        ms[0] = len(head.content)
        for i, body in enumerate(bodies):
            ms[2 * i + 1] = len(body.head)
            ms[2 * i + 2] = len(body.content)
        ms[-1] = len(foot.content)

        # TODO: put this in a method. applying np.split(array_of_all_rows, idxs_split) would break it back into list of head, bodies, foot
        # idxs_split = np.cumsum(ms)[:-1]
        m = ms.sum()

        shape = [m, n]
        icas_row = np.empty(m, dtype='O')
        icas = np.empty(shape, dtype='O')
        aligns = np.zeros(shape, dtype=np.int8)
        cells = np.empty(shape, dtype='O')
        for i, row in enumerate(chain(
            head.content,
            *sum(([body.head, body.content] for body in bodies), []),
            foot.content,
        )):
            icas_row[i] = Ica(row.identifier, row.classes, row.attributes)
            j = 0
            for cell in row.content:
                # determine j
                while cells[i, j] is not None:
                    j += 1

                rowspan: int = cell.rowspan
                colspan: int = cell.colspan
                if rowspan == 1 and colspan == 1:
                    pan_cell = PanCellPlain(cell.content)
                    cells[i, j] = PanCellPlain(cell.content)
                else:
                    pan_cell = PanCellBlock(cell.content, (rowspan, colspan), (i, j))
                    pan_cell.put_array(cells)

                icas[i, j] = Ica(cell.identifier, cell.classes, cell.attributes)
                aligns[i, j] = ALIGN_TO_IDX[cell.alignment[5]]

        return cls(
            ica_table,
            short_caption, caption,
            spec,
            shape,
            ms, ns_head,
            icas_body,
            icas_row,
            icas,
            aligns,
            cells,
        )

    def to_ascii_table(self, width: int = 15) -> str:
        '''print the table as ascii table

        :param int width: width per column
        '''
        from textwrap import wrap

        from terminaltables import AsciiTable

        return AsciiTable([
            [
                '\n'.join(wrap(
                    stringify(TableCell(*cell.content)),
                    width,
                ))
            for cell in row
            ]
            for row in self.cells
        ]).table
