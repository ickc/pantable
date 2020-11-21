from __future__ import annotations

import sys
from typing import Union, List, Tuple, Optional, Dict
from itertools import chain
from pprint import pformat
from fractions import Fraction
from abc import ABC, abstractmethod

if (sys.version_info.major, sys.version_info.minor) < (3, 8):
    try:
        from backports.cached_property import cached_property
    except ImportError:
        raise ImportError('Using Python 3.6 or 3.7? Please run "pip install backports.cached_property".')
else:
    from functools import cached_property

import numpy as np

from panflute.table_elements import Table, TableCell, Caption, TableHead, TableFoot, TableRow, TableBody
from panflute.elements import CodeBlock, Doc
from panflute.containers import ListContainer
from panflute.tools import stringify, convert_text

try:
    from dataclasses import dataclass, field, fields
except ImportError:
    raise ImportError('Using Python 3.6? Please run `pip install dataclasses` or `conda install dataclasses`.')

from .util import get_first_type

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

# CodeBlock


@dataclass
class PanTableOption:
    '''options in CodeBlock table

    remember that the keys in YAML sometimes uses hyphen/underscore
    and here uses underscore
    '''
    caption: Optional[str] = None
    alignment: Optional[str] = None
    width: Optional[List[float]] = None
    table_width: float = 1.
    header: bool = True
    markdown: bool = False
    include: Optional[str] = None
    include_encoding: Optional[str] = None
    csv_kwargs: dict = field(default_factory=dict)

    def __post_init__(self):
        '''fall back to default if invalid type

        Only check for type here. e.g. positivity of width and table_width are not checked at this point.
        '''
        types = get_first_type(self.__class__)
        for field_ in fields(self):
            key = field_.name
            value = getattr(self, key)
            type_ = types[key]
            # special case: default factory
            default = dict() if key == 'csv_kwargs' else field_.default
            # wrong type and not default
            if not (value == default or isinstance(value, type_)):
                # special case: Fraction/int
                try:
                    if key == 'table_width':
                        value = float(Fraction(value))
                        self.table_width = value
                        continue
                except (ValueError, TypeError):
                    pass
                print(f"Option {key.replace('_', '-')} with value {value} has invalid type and set to default: {default}", file=sys.stderr)
                setattr(self, key, default)
        # check Optional[List[float]]
        if self.width is not None:
            try:
                self.width = [float(Fraction(x)) for x in self.width]
            except (ValueError, TypeError):
                print(f'Option width with value {self.width} has invalid type and set to default: None', file=sys.stderr)
                self.width = None

    @classmethod
    def from_kwargs(cls, **kwargs):
        return cls(**{
            key_underscored: value
            for key, value in kwargs.items()
            if (key_underscored := str(key).replace('-', '_')) in cls.__annotations__
        })


class PanTableCodeBlock:

    '''A PanTable representation of CodeBlock

    it handles the transition between panflute CodeBlock and PanTable

    It can convert to and from panflute CodeBlock,
    and to and from PanTable
    '''

    def __init__(self, options: dict, data: str, element: CodeBlock, doc: Doc = None):
        '''
        these args are those passed from within yaml_filter
        '''
        self.options = PanTableOption.from_kwargs(**options)
        self.data = data
        self.ica = Ica(
            identifier=element.identifier,
            classes=element.classes,
            attributes=element.attributes,
        )

    def csv_to_pantable(self):
        '''parse data as csv and return a PanTable
        '''
        return PanTable(
            self.ica,
            short_caption, caption,
            spec,
            ms, n, ns_head,
            icas_rowblock,
            icas_row,
            icas,
            aligns,
            cells,
        )

# Table


@dataclass
class Ica:
    """a class of identifier, classes, and attributes"""
    identifier: str = ''
    classes: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)


class FakeRepr:
    '''mixin for repr that doesn't yield itself after eval, from to_dict method
    '''

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        '''TODO'''
        return pformat(self.to_dict(), sort_dicts=False, compact=False, width=-1)

    def to_dict(self):
        raise NotImplementedError


class AlignText:
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
    def from_panflute_ast(cls, table: Table):
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


class PanCell:
    '''a class of simple cell within PanTable
    '''
    shape = (1, 1)
    idxs: Optional[Tuple[int, int]] = None

    def __init__(self, content: Union[ListContainer, str]):
        self.content = content

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return repr(self.content)

    def is_at(self, loc) -> bool:
        return True


class PanCellBlock(PanCell):
    '''a class of Block cell within PanTable
    '''
    def __init__(
        self,
        content: Union[ListContainer, str],
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


class PanTableAbstract(ABC, FakeRepr, AlignText):
    '''an abstract class of PanTables
    '''

    def __init__(
        self,
        ica_table: Ica,
        short_caption, caption,
        spec: Spec,
        ms: np.ndarray[np.int64], n: int, ns_head: np.ndarray[np.int64],
        icas_rowblock: np.ndarray,
        icas_row: np.ndarray,
        icas: np.ndarray,
        aligns: np.ndarray,
        cells: np.ndarray,
    ):
        self.ica_table = ica_table
        self.short_caption = short_caption
        self.caption = caption
        self.spec = spec
        self._ms = ms
        self.n = n
        self.ns_head = ns_head
        self.icas_rowblock = icas_rowblock
        self.icas_row = icas_row
        self.icas = icas
        self.aligns = aligns
        self.cells = cells

    def __str__(self, width: int = 15, cannonical=True, tablefmt='grid') -> str:
        '''print the table as ascii table

        :param int width: width per column
        :param str tablefmt: in ('plain', 'simple', 'grid', 'fancy_grid', 'pipe', 'orgtbl', 'rst', 'mediawiki', 'html', 'latex', 'latex_raw', 'latex_booktabs', 'tsv')
        '''
        try:
            from tabulate import tabulate

            return tabulate(
                self.cells_stringified(width=width, cannonical=cannonical),
                tablefmt=tablefmt,
                headers=() if self.ms[0] == 0 else "firstrow",
            )
        except ImportError:
            print('Consider having a better str by `pip install tabulate` or `conda install tabulate`.', file=sys.stderr)
            return self.__repr__()

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
            'icas_rowblock': self.icas_rowblock,
            'icas_row': self.icas_row,
            'icas': self.icas,
            'aligns': self.aligns_text,
            'cells': self.cells,
        }

    @abstractmethod
    def cells_stringified(self, width: int = 15, cannonical=True) -> np.ndarray[str]:
        '''return stringified cells

        :param int width: width per column
        '''
        return ''

    @property
    def shape(self) -> Tuple[int, int]:
        return (self._ms.sum(), self.n)

    @property
    def m_bodies(self) -> int:
        return self.ns_head.size

    @property
    def m_rowblocks(self) -> int:
        return self._ms.size

    @property
    def ica_head(self) -> Ica:
        return self.icas_rowblock[0]

    @property
    def icas_body(self) -> np.ndarray[Ica]:
        return self.icas_rowblock[1:-1]

    @property
    def ica_foot(self) -> Ica:
        return self.icas_rowblock[-1]

    @property
    def ms(self) -> np.ndarray[np.int64]:
        return self._ms

    @ms.setter
    def ms(self, ms):
        del self.rowblock_idxs_row
        del self.rowblock_splitting_idxs
        del self.is_heads
        del self.is_foots
        del self.is_body_heads
        del self.is_body_bodies
        del self.body_idxs_row
        self._ms = ms

    @cached_property
    def rowblock_idxs_row(self) -> np.ndarray[np.int64]:
        '''reverse lookup the index of rowblocks per row
        '''
        return np.digitize(np.arange(self.shape[0]), np.cumsum(self._ms))

    @cached_property
    def is_heads(self) -> np.ndarray[np.bool_]:
        return self.rowblock_idxs_row == 0

    @cached_property
    def is_foots(self) -> np.ndarray[np.bool_]:
        return self.rowblock_idxs_row == (self._ms.size - 1)

    @cached_property
    def is_body_heads(self) -> np.ndarray[np.bool_]:
        maybe_body_heads = self.rowblock_idxs_row % 2 == 1
        return (~self.is_foots) & maybe_body_heads

    @cached_property
    def is_body_bodies(self) -> np.ndarray[np.bool_]:
        return ~(self.is_heads | self.is_foots | self.is_body_heads)

    @cached_property
    def body_idxs_row(self) -> np.ndarray[np.int64]:
        '''calculate the i-th body that each row belongs to

        negative values means the row is not in a body
        '''
        body_idxs_row = (self.rowblock_idxs_row - 1) // 2
        body_idxs_row[self.is_foots] = -1
        return body_idxs_row

    @cached_property
    def rowblock_splitting_idxs(self) -> np.ndarray[np.int64]:
        '''applying np.split(array_of_rows, rowblock_splitting_idxs) would break it back into list of head, bodies, foot
        '''
        return np.cumsum(self._ms)[:-1]

    def iter_rowblocks(self, array: np.ndarray) -> List[np.ndarray]:
        '''break array into list of head, bodies, foot

        assume array is iterables of rows
        '''
        return np.split(array, self.rowblock_splitting_idxs)

    def iterrows(self):
        '''TODO'''
        rowblock_idxs_row = self.rowblock_idxs_row
        is_heads = self.is_heads
        is_foots = self.is_foots
        is_body_heads = self.is_body_heads
        is_body_bodies = self.is_body_bodies
        body_idxs_row = self.body_idxs_row

        res = []
        for i in range(self.shape[0]):
            idx_block = rowblock_idxs_row[i]
            is_head = is_heads[i]
            is_body_head = is_body_heads[i]
            is_body_body = is_body_bodies[i]
            is_foot = is_foots[i]
            idx_body = body_idxs_row[i]
            idx_body = None if idx_body < 0 else idx_body
            res.append({
                'is_head': is_head,
                'is_body_head': is_body_head,
                'is_body_body': is_body_body,
                'is_foot': is_foot,
                'idx_body': idx_body,
                'n_head': None if idx_body is None else self.ns_head[idx_body],
                'ica_row_block': self.icas_rowblock[idx_block],
                'ica_row': self.icas_row[i],
                'icas': self.icas[i],
                'aligns': self.aligns[i],
                'cells': self.cells[i]
            })
        return res

    @property
    def cells_cannonical(self) -> np.ndarray[PanCell]:
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


class PanTable(PanTableAbstract):
    '''a representation of panflute Table

    All PanCell in cells should have content type as ListContainer
    although not strictly enforced here
    '''

    def __init__(
        self,
        ica_table: Ica,
        short_caption: Optional[ListContainer], caption: ListContainer,
        spec: Spec,
        ms: np.ndarray[np.int64], n: int, ns_head: np.ndarray[np.int64],
        icas_rowblock: np.ndarray[Ica],
        icas_row: np.ndarray[Ica],
        icas: np.ndarray[Ica],
        aligns: np.ndarray[np.int8],
        cells: np.ndarray[PanCell],
    ):
        self.ica_table = ica_table
        self.short_caption = short_caption
        self.caption = caption
        self.spec = spec
        self._ms = ms
        self.n = n
        self.ns_head = ns_head
        self.icas_rowblock = icas_rowblock
        self.icas_row = icas_row
        self.icas = icas
        self.aligns = aligns
        self.cells = cells

    def _repr_html_(self) -> str:
        return convert_text(self.to_panflute_ast(), input_format='panflute', output_format='html')

    @staticmethod
    def iter_tablerows(
        icas_row: np.ndarray[Ica],
        pf_cells: np.ndarray[TableCell],
    ) -> List[TableRow]:
        return (
            TableRow(
                *[i for i in pf_row_array if i is not None],
                identifier=ica.identifier,
                classes=ica.classes,
                attributes=ica.attributes
            )
            for ica, pf_row_array in zip(icas_row, pf_cells)
        )

    def cells_stringified(self, width: int = 15, cannonical=True) -> np.ndarray[str]:
        '''return stringified cells

        :param int width: width per column
        '''
        from textwrap import wrap

        cells = self.cells
        res = np.empty_like(cells)
        m, n = cells.shape
        for i in range(m):
            for j in range(n):
                cell = cells[i, j]
                if cannonical:
                    cell = cell if cell.is_at((i, j)) else None
                res[i, j] = '' if cell is None else '\n'.join(wrap(
                    stringify(TableCell(*cell.content)),
                    width,
                ))
        return res

    @property
    def panflute_tablecells(self) -> np.ndarray[TableCell]:
        cells = self.cells_cannonical
        cells_flat = cells.ravel()
        icas_flat = self.icas.ravel()
        aligns_flat = self.aligns_text.ravel()

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

    @classmethod
    def from_panflute_ast(cls, table: Table):
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
        m_bodies = len(bodies)
        ns_head = np.empty(m_bodies, dtype=np.int64)
        icas_rowblock = np.empty(m_bodies + 2, dtype='O')
        icas_rowblock[0] = Ica(head.identifier, head.classes, head.attributes)
        for i, body in enumerate(bodies):
            ns_head[i] = body.row_head_columns
            icas_rowblock[i + 1] = Ica(body.identifier, body.classes, body.attributes)
        icas_rowblock[i + 2] = Ica(foot.identifier, foot.classes, foot.attributes)

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

        shape = (m, n)
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
                    cells[i, j] = PanCell(cell.content)
                else:
                    pan_cell = PanCellBlock(cell.content, (rowspan, colspan), (i, j))
                    pan_cell.put(cells)

                icas[i, j] = Ica(cell.identifier, cell.classes, cell.attributes)
                aligns[i, j] = ALIGN_TO_IDX[cell.alignment[5]]

        return cls(
            ica_table,
            short_caption, caption,
            spec,
            ms, n, ns_head,
            icas_rowblock,
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

        icas_row_by_blocks = self.iter_rowblocks(self.icas_row)
        pf_cells_by_blocks = self.iter_rowblocks(self.panflute_tablecells)

        # head
        ica_block = self.icas_rowblock[0]
        icas_rowblock = icas_row_by_blocks[0]
        pf_cells_block = pf_cells_by_blocks[0]
        content = self.iter_tablerows(icas_rowblock, pf_cells_block)
        head = TableHead(*content, identifier=ica_block.identifier, classes=ica_block.classes, attributes=ica_block.attributes)
        # bodies
        bodies = []
        for i in range(self.m_bodies):
            row_head_columns = int(self.ns_head[i])
            # offset 1 as 1st is head
            ica_block = self.icas_rowblock[1 + i]
            temp = []
            for j in range(2):
                # offset 1 as 1st is head
                # 2 * i as 2 elements per body
                # 1st is body-head, 2nd is body-body
                idx_body = 1 + 2 * i + j
                icas_rowblock = icas_row_by_blocks[idx_body]
                pf_cells_block = pf_cells_by_blocks[idx_body]
                temp.append(self.iter_tablerows(icas_rowblock, pf_cells_block))
            bodies.append(TableBody(
                *temp[1],
                head=temp[0],
                row_head_columns=row_head_columns,
                identifier=ica_block.identifier,
                classes=ica_block.classes,
                attributes=ica_block.attributes,
            ))
        # foot
        ica_block = self.icas_rowblock[-1]
        icas_rowblock = icas_row_by_blocks[-1]
        pf_cells_block = pf_cells_by_blocks[-1]
        content = self.iter_tablerows(icas_rowblock, pf_cells_block)
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


class PanTableStr(PanTableAbstract):
    '''similar to PanTable, but with panflute ASTs as str

    All PanCell in cells should have content type as str
    although not strictly enforced here
    '''

    def __init__(
        self,
        ica_table: Ica,
        short_caption: Optional[str], caption: str,
        spec: Spec,
        ms: np.ndarray[np.int64], n: int, ns_head: np.ndarray[np.int64],
        icas_rowblock: np.ndarray[str],
        icas_row: np.ndarray[str],
        icas: np.ndarray[str],
        aligns: np.ndarray[np.int8],
        cells: np.ndarray[PanCell],
    ):
        self.ica_table = ica_table
        self.short_caption = short_caption
        self.caption = caption
        self.spec = spec
        self._ms = ms
        self.n = n
        self.ns_head = ns_head
        self.icas_rowblock = icas_rowblock
        self.icas_row = icas_row
        self.icas = icas
        self.aligns = aligns
        self.cells = cells

    def _repr_html_(self) -> str:
        return self.__str__(tablefmt='html')

    def cells_stringified(self, width: int = 15, cannonical=True) -> np.ndarray[str]:
        '''return stringified cells

        :param int width: width per column
        '''
        from textwrap import wrap

        cells = self.cells
        res = np.empty_like(cells)
        m, n = cells.shape
        for i in range(m):
            for j in range(n):
                cell = cells[i, j]
                if cannonical:
                    cell = cell if cell.is_at((i, j)) else None
                res[i, j] = '' if cell is None else '\n'.join(wrap(
                    cell.content,
                    width,
                ))
        return res
