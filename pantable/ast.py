from __future__ import annotations

import sys
from typing import Union, List, Tuple, Optional
from itertools import chain
from pprint import pformat

if (sys.version_info.major, sys.version_info.minor) < (3, 8):
    try:
        from backports.cached_property import cached_property
    except ImportError:
        raise ImportError('Using Python 3.6 or 3.7? Please run "pip install backports.cached_property".')
else:
    from functools import cached_property

import numpy as np

from panflute.table_elements import Table, TableCell, Caption, TableHead, TableFoot, TableRow, TableBody
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


class AlignText():
    '''a mixin for getting aligns_text from aligns
    '''

    aligns: np.ndarray[np.int8]

    @property
    def aligns_text(self) -> np.ndarray[np.str_]:
        return ALIGN[self.aligns]


class Spec(FakeRepr, AlignText):
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

    def to_panflute_ast(self) -> List[Tuple]:
        return [
            (align, COLWIDTHDEFAULT if np.isnan(width) else width)
            for align, width in zip(self.aligns_text, self.col_widths)
        ]


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

    def is_at(self, loc) -> bool:
        return True


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

    def put(self, array, overwrite=False):
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

    def is_at(self, loc: Tuple[int, int]) -> bool:
        return loc == self.idxs


def pancell_to_panflute_tablecell(
    icas: np.ndarray[Ica],
    aligns_text: np.ndarray,
    cells: np.ndarray[PanCellPlain],
) -> np.ndarray[TableCell]:
    icas_flat = icas.ravel()
    aligns_flat = aligns_text.ravel()
    cells_flat = cells.ravel()

    res = np.empty_like(cells)
    res_flat = res.ravel()
    for i in range(res_flat.size):
        cell = cells_flat[i]
        if cell is None:
            res_flat[i] = None
        else:
            rowspan, colspan = cell.shape
            ica = icas_flat[i]
            res_flat[i] = TableCell(
                *cell.content,
                alignment=aligns_flat[i],
                rowspan=rowspan,
                colspan=colspan,
                identifier=ica.identifier,
                classes=ica.classes,
                attributes=ica.attributes,
            )
    return res


class PanTable(FakeRepr, AlignText):
    '''a representation of panflute Table
    '''

    def __init__(
        self,
        ica_table: Ica,
        short_caption: Union[ListContainer, None], caption: ListContainer,
        spec: Spec,
        shape: List[int],
        ms: np.ndarray[np.int64], ns_head: np.ndarray[np.int64],
        icas_row_block: np.ndarray[Ica],
        icas_row: np.ndarray[Ica],
        icas: np.ndarray[Ica],
        aligns: np.ndarray[np.int8],
        cells: np.ndarray[PanCellPlain],
    ):
        self.ica_table = ica_table
        self.short_caption = short_caption
        self.caption = caption
        self.spec = spec
        self.shape = shape
        self._ms = ms
        self.ns_head = ns_head
        self.icas_row_block = icas_row_block
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
            'icas_row_block': self.icas_row_block,
            'icas_row': self.icas_row,
            'icas': self.icas,
            'aligns': self.aligns_text,
            'cells': self.cells,
        }

    @property
    def n_bodies(self) -> int:
        return self.ns_head.size

    @property
    def ica_head(self) -> Ica:
        return self.icas_row_block[0]

    @property
    def icas_body(self) -> np.ndarray[Ica]:
        return self.icas_row_block[1:-1]

    @property
    def ica_foot(self) -> Ica:
        return self.icas_row_block[-1]

    @property
    def ms(self) -> np.ndarray[np.int64]:
        return self._ms

    @ms.setter
    def ms(self, ms):
        del self.idxs_ms
        del self.idxs_split
        del self.is_heads
        del self.is_foots
        del self.is_body_heads
        del self.is_body_bodies
        del self.idxs_body
        self._ms = ms
        self.shape[0] = ms.sum()

    @cached_property
    def idxs_ms(self) -> np.ndarray[np.int64]:
        '''reverse lookup the index of rows in blocks of ms
        '''
        return np.digitize(np.arange(self.shape[0]), np.cumsum(self.ms))

    @cached_property
    def is_heads(self) -> np.ndarray[np.bool_]:
        return self.idxs_ms == 0

    @cached_property
    def is_foots(self) -> np.ndarray[np.bool_]:
        return self.idxs_ms == (self.ms.size - 1)

    @cached_property
    def is_body_heads(self) -> np.ndarray[np.bool_]:
        maybe_body_heads = self.idxs_ms % 2 == 1
        return (~self.is_foots) & maybe_body_heads

    @cached_property
    def is_body_bodies(self) -> np.ndarray[np.bool_]:
        return ~(self.is_heads | self.is_foots | self.is_body_heads)

    @cached_property
    def idxs_body(self) -> np.ndarray[np.int64]:
        '''calculate the i-th body that each row belongs to

        negative values means the row is not in a body
        '''
        idxs_body = (self.idxs_ms - 1) // 2
        idxs_body[self.is_foots] = -1
        return idxs_body

    @cached_property
    def idxs_split(self) -> np.ndarray[np.int64]:
        '''applying np.split(array_of_all_rows, idxs_split) would break it back into list of head, bodies, foot
        '''
        return np.cumsum(self.ms)[:-1]

    def iter_row_blocks(self, array: np.ndarray) -> List[np.ndarray]:
        '''break array into list of head, bodies, foot

        assume array is iterables of rows
        '''
        return np.split(array, self.idxs_split)

    def iterrows(self):
        idxs_ms = self.idxs_ms
        is_heads = self.is_heads
        is_foots = self.is_foots
        is_body_heads = self.is_body_heads
        is_body_bodies = self.is_body_bodies
        idxs_body = self.idxs_body

        res = []
        for i in range(self.shape[0]):
            idx_block = idxs_ms[i]
            is_head = is_heads[i]
            is_body_head = is_body_heads[i]
            is_body_body = is_body_bodies[i]
            is_foot = is_foots[i]
            idx_body = idxs_body[i]
            idx_body = None if idx_body < 0 else idx_body
            res.append({
                'is_head': is_head,
                'is_body_head': is_body_head,
                'is_body_body': is_body_body,
                'is_foot': is_foot,
                'idx_body': idx_body,
                'n_head': None if idx_body is None else self.ns_head[idx_body],
                'ica_row_block': self.icas_row_block[idx_block],
                'ica_row': self.icas_row[i],
                'icas': self.icas[i],
                'aligns': self.aligns[i],
                'cells': self.cells[i]
            })
        return res

    @staticmethod
    def iter_tablerow(
        icas_row: np.ndarray[Ica],
        pf_cells: np.ndarray[TableCell],
    ) -> List[TableRow]:
        return [
            TableRow(
                *[i for i in pf_row_array if i is not None],
                identifier=ica.identifier,
                classes=ica.classes,
                attributes=ica.attributes
            )
            for ica, pf_row_array in zip(icas_row, pf_cells)
        ]

    @property
    def cells_cannonical(self) -> np.ndarray[PanCellPlain]:
        '''return a cell array where spanned cells appeared in cannonical location only

        top-left corner of the grid is the cannonical location of a spanned cell
        '''
        cells = self.cells
        res = np.empty_like(cells)
        m, n = cells.shape
        for i in range(m):
            for j in range(n):
                cell = cells[i, j]
                res[i, j] = cell if cell.is_at((i, j)) else None
        return res

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
        foot = table.foot

        bodies = table.content
        n_bodies = len(bodies)
        ns_head = np.empty(n_bodies, dtype=np.int64)
        icas_row_block = np.empty(n_bodies + 2, dtype='O')
        icas_row_block[0] = Ica(head.identifier, head.classes, head.attributes)
        for i, body in enumerate(bodies):
            ns_head[i] = body.row_head_columns
            icas_row_block[i + 1] = Ica(body.identifier, body.classes, body.attributes)
        icas_row_block[i + 2] = Ica(foot.identifier, foot.classes, foot.attributes)

        # there are 1 head,
        # then n bodies, for each body one head and one content,
        # then 1 foot
        ms = np.empty(2 * len(bodies) + 2, dtype=np.int64)
        ms[0] = len(head.content)
        for i, body in enumerate(bodies):
            ms[2 * i + 1] = len(body.head)
            ms[2 * i + 2] = len(body.content)
        ms[-1] = len(foot.content)

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
                    cells[i, j] = PanCellPlain(cell.content)
                else:
                    pan_cell = PanCellBlock(cell.content, (rowspan, colspan), (i, j))
                    pan_cell.put(cells)

                icas[i, j] = Ica(cell.identifier, cell.classes, cell.attributes)
                aligns[i, j] = ALIGN_TO_IDX[cell.alignment[5]]

        return cls(
            ica_table,
            short_caption, caption,
            spec,
            shape,
            ms, ns_head,
            icas_row_block,
            icas_row,
            icas,
            aligns,
            cells,
        )

    def to_panflute_ast(self) -> Table:
        caption = Caption(
            *self.caption,
            short_caption=self.short_caption,
        )

        colspec = self.spec.to_panflute_ast()

        icas_row_by_blocks = self.iter_row_blocks(self.icas_row)
        pf_cells_by_blocks = self.iter_row_blocks(pancell_to_panflute_tablecell(
            self.icas,
            self.aligns_text,
            self.cells_cannonical,
        ))

        # head
        ica_block = self.icas_row_block[0]
        icas_row_block = icas_row_by_blocks[0]
        pf_cells_block = pf_cells_by_blocks[0]
        content = self.iter_tablerow(icas_row_block, pf_cells_block)
        head = TableHead(*content, identifier=ica_block.identifier, classes=ica_block.classes, attributes=ica_block.attributes)
        # bodies
        bodies = []
        for i in range(self.n_bodies):
            row_head_columns = int(self.ns_head[i])
            # offset 1 as 1st is head
            ica_block = self.icas_row_block[1 + i]
            temp = []
            for j in range(2):
                # offset 1 as 1st is head
                # 2 * i as 2 elements per body
                # 1st is body-head, 2nd is body-body
                idx_body = 1 + 2 * i + j
                icas_row_block = icas_row_by_blocks[idx_body]
                pf_cells_block = pf_cells_by_blocks[idx_body]
                temp.append(self.iter_tablerow(icas_row_block, pf_cells_block))
            bodies.append(TableBody(
                *temp[1],
                head=temp[0],
                row_head_columns=row_head_columns,
                identifier=ica_block.identifier,
                classes=ica_block.classes,
                attributes=ica_block.attributes,
            ))
        # foot
        ica_block = self.icas_row_block[-1]
        icas_row_block = icas_row_by_blocks[-1]
        pf_cells_block = pf_cells_by_blocks[-1]
        content = self.iter_tablerow(icas_row_block, pf_cells_block)
        foot = TableFoot(*content, identifier=ica_block.identifier, classes=ica_block.classes, attributes=ica_block.attributes)

        return Table(
            *bodies,
            head=head,
            foot=foot,
            caption=caption,
            colspec=colspec,
            identifier=self.ica_table.identifier,
            classes=self.ica_table.classes,
            attributes=self.ica_table.attributes,
        )

    def to_ascii_table(self, width: int = 15, cannonical=True) -> str:
        '''print the table as ascii table

        :param int width: width per column
        '''
        from textwrap import wrap

        from terminaltables import AsciiTable

        return AsciiTable([
            [
                '' if cell is None else '\n'.join(wrap(
                    stringify(TableCell(*cell.content)),
                    width,
                ))
                for cell in row
            ]
            for row in (self.cells_cannonical if cannonical else self.cells)
        ]).table
