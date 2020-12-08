from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING, Union, List, Optional, Type
from itertools import chain, repeat
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
try:
    from dataclasses import dataclass, field, fields
except ImportError:
    raise ImportError('Using Python 3.6? Please run `pip install dataclasses` or `conda install dataclasses`.')

if TYPE_CHECKING:
    from typing import Tuple, Dict, Iterator, Set

    from panflute.base import Inline, Block
    from panflute.elements import Doc

import numpy as np
import yaml

from panflute.table_elements import Table, TableCell, Caption, TableHead, TableFoot, TableRow, TableBody
from panflute.elements import CodeBlock, Plain, Span, Str, Para
from panflute.containers import ListContainer
from panflute.tools import stringify, convert_text

from .util import get_types, get_yaml_dumper, iter_convert_texts_panflute_to_markdown, iter_convert_texts_markdown_to_panflute
from .io import load_csv_array, dump_csv_io

COLWIDTHDEFAULT = 'ColWidthDefault'


def single_para_to_plain(elem: ListContainer) -> ListContainer:
    '''convert single element to Plain

    if `elem` is a ListContainer of a single element, then convert it to a ListContainer of Plain and return that.
    Else return `elem`.
    '''
    if len(elem) == 1:
        return ListContainer(Plain(*elem[0].content))
    else:
        return elem


# CodeBlock


@dataclass
class PanTableOption:
    '''options in CodeBlock table

    remember that the keys in YAML sometimes uses hyphen/underscore
    and here uses underscore
    '''
    short_caption: str = ''
    caption: str = ''
    alignment: str = ''
    alignment_cells: str = ''
    width: Optional[List[Union[float, str]]] = None
    table_width: Optional[float] = None
    header: bool = True
    ms: Optional[List[int]] = None
    ns_head: Optional[List[int]] = None
    markdown: bool = False
    fancy_table: bool = False
    include: str = ''
    include_encoding: str = ''
    format: str = 'csv'
    csv_kwargs: dict = field(default_factory=dict)

    def __post_init__(self):
        '''fall back to default if invalid type

        Only check for type here. e.g. positivity of width and table_width are not checked at this point.
        '''
        types_dict = get_types(self.__class__)
        for field_ in fields(self):
            key = field_.name
            value = getattr(self, key)
            types = types_dict[key]
            # special case: default factory
            default = dict() if key == 'csv_kwargs' else field_.default
            # wrong type and not default
            if not (value == default or isinstance(value, types)):
                # special case: Fraction/int
                try:
                    if key == 'table_width':
                        value = float(Fraction(value))
                        self.table_width = value
                    else:
                        # cast it into first type
                        setattr(self, key, types[0](value))
                except (ValueError, TypeError):
                    print(f"Option {key.replace('_', '-')} with value {value} has invalid type and set to default: {default}", file=sys.stderr)
                    setattr(self, key, default)
        # width: Optional[List[Union[float, str]]] is not checked here
        # * i.e. we only guarantee width is Optional[list] so far
        # see normalize
        # check Optional[List[int]]
        for key in ('ms', 'ns_head'):
            value = getattr(self, key)
            if value is not None:
                try:
                    setattr(self, key, [int(x) for x in value])
                except (ValueError, TypeError):
                    print(f"Option {key.replace('_', '-')} with value {value} has invalid type and set to default: None", file=sys.stderr)
                    setattr(self, key, None)

    def normalize(self, shape: Tuple[int, int]):
        '''normalize

        assume the types are correct. Normalize what's beyond type-correctness.

        e.g. from PanCodeBlock to PanTableStr should uses this
        '''
        m, n = shape

        # set all str or negative width to default
        sum_ = 0.
        width = self.width
        if width is not None:
            widths: List[Union[float, str]] = ['D'] * n
            for i, width_ in enumerate(width):
                if i >= n:
                    break
                try:
                    temp = float(Fraction(width_))
                    if temp >= 0.:
                        widths[i] = temp
                        sum_ += temp
                except (ValueError, TypeError):
                    pass
            self.width = widths

        table_width = self.table_width
        # set table_width to default if smaller than sum of positive width
        if table_width is not None and table_width < sum_:
            print(f'table-width smaller than sum of width: {sum_}. Set to default.', file=sys.stderr)
            self.table_width = None

        ms = self.ms
        ms_sum = 0
        if ms is not None:
            try:
                l = len(ms)
                if l < 4:
                    raise ValueError(f'ms is too short, set to default: {ms}')
                if l % 2 != 0:
                    raise ValueError(f'ms is not of even length, set to default: {ms}')
                for m_ in ms:
                    if m_ >= 0:
                        ms_sum += m_
                    else:
                        raise ValueError(f'ms cannot be negative, set to default: {ms}')
                if ms_sum != m:
                    raise ValueError(f'Sum of ms {ms} does not equal no of rows {m}, set to default.')
            except ValueError as e:
                print(e, file=sys.stderr)
                self.ms = None
                ms = None

        m_body = 1 if ms is None else len(ms) // 2 - 1
        ns_head = self.ns_head
        if ns_head is not None:
            try:
                l = len(ns_head)
                if l != m_body:
                    raise ValueError(f'ns_head {ns_head} should be of length as no. of bodies {m_body}, set to default.')
                for n_ in ns_head:
                    if n_ > n:
                        raise ValueError(f'ns_head {ns_head} cannot be larger than no. of columns {n}, set to default.')
            except ValueError as e:
                print(e, file=sys.stderr)
                self.ns_head = None

    def simplify(self):
        '''Reduced equivalent attrs to simplest form

        e.g. from PanTableStr to PanCodeBlock should uses this
        '''
        # alignment: simplify LRCD...D to LRC
        alignment = self.alignment
        last_idx = -1
        for i, char in enumerate(alignment):
            if char != 'D':
                last_idx = i
        self.alignment = alignment[:last_idx + 1]

        # alignment_cells
        align_list = self.alignment_cells.split('\n')
        last_idx = -1
        last_idy = -1
        for i, alignment in enumerate(align_list):
            for j, char in enumerate(alignment):
                if char != 'D':
                    last_idx = i
                    last_idy = j
        self.alignment_cells = '\n'.join(line[:last_idy + 1] for line in align_list[:last_idx + 1])

        # width
        widths = self.width
        if widths is not None:
            default = True
            for width in widths:
                if width != 'D':
                    default = False
                    break
            if default:
                self.width = None
            else:
                for i, width in enumerate(widths):
                    # convert float to Fraction if lossless
                    temp = str(Fraction(width).limit_denominator())
                    if float(Fraction(temp)) == width:
                        widths[i] = temp

        # header & ms
        # single body, no foot, header of one row or below
        # is special case of header = True/False
        ms = self.ms
        if ms is not None:
            if len(ms) == 4 and ms[1] == 0 and ms[3] == 0:
                if ms[0] == 1:
                    self.ms = None
                    self.header = True
                elif ms[0] == 0:
                    self.ms = None
                    self.header = False

        # ns_head
        # if all zero that equiv. to None
        ns_head = self.ns_head
        default = True
        for n in ns_head:
            if n != 0:
                default = False
                break
        if default:
            self.ns_head = None

    @classmethod
    def from_kwargs(cls, **kwargs) -> PanTableOption:
        return cls(**{
            key_underscored: value
            for key, value in kwargs.items()
            if (key_underscored := str(key).replace('-', '_')) in cls.__annotations__
        })

    @property
    def kwargs(self) -> dict:
        '''to dict without the defaults

        expect `self.from_kwargs(**self.kwargs) == self`
        '''
        return {
            key.replace('_', '-'): value
            for field_ in fields(self)
            # check value == default
            if (
                value := getattr(self, (key := field_.name))
            ) != (
                dict()
                # special case: default factory
                if key == 'csv_kwargs' else
                field_.default
            )
        }

    @staticmethod
    def to_align_1d(alignment: str, size: int) -> Align:
        alignment_norm = alignment.strip().upper()
        try:
            aligns_char = np.fromiter(alignment_norm, dtype='S1')
            aligns_char_size = aligns_char.size
            if aligns_char_size >= size:
                aligns = Align.from_aligns_char(aligns_char[:size])
            elif aligns_char_size < size:
                aligns = Align.default(shape=(size,))
                aligns.aligns[:aligns_char_size] = Align.from_aligns_char(aligns_char).aligns
        except UnicodeEncodeError:
            print(f'Non-ASCII character detected in {alignment}, ignoring and set to default.', file=sys.stderr)
            aligns = Align.default(shape=(size,))
        return aligns

    @staticmethod
    def to_align_2d(alignment_cells: str, shape: Tuple[int, int]) -> Align:
        m, n = shape
        res = Align.default(shape)
        aligns = res.aligns
        for i, row in enumerate(alignment_cells.strip().split('\n')):
            # in case where no. of rows is more than needed
            if i >= m:
                break
            aligns[i] = PanTableOption.to_align_1d(row, n).aligns
        return res

    def alignment_to_align(self, size: int) -> Align:
        return self.to_align_1d(self.alignment, size)

    def alignment_cells_to_align(self, shape: Tuple[int, int]) -> Align:
        return self.to_align_2d(self.alignment_cells, shape)

    def to_spec(self, size: int) -> Spec:
        '''to Spec

        assume normalized self.
        '''
        width = self.width

        if width is None:
            col_widths = None
        else:
            col_widths = np.full(size, np.nan, dtype=np.float64)
            for i in range(size):
                temp = width[i]
                if type(temp) != str:
                    col_widths[i] = temp
        return Spec(
            self.alignment_to_align(size),
            col_widths=col_widths
        )


class PanCodeBlock:

    '''A PanTable representation of CodeBlock

    it handles the transition between panflute CodeBlock and PanTable

    It can convert to and from panflute CodeBlock,
    and to and from PanTable

    there's no `from_panflute_ast` method, as we expect the args in the
    `__init__` to be from `panflute.yaml_filter` directly.

    c.f. `.util.parse_markdown_codeblock` for testing purposes
    '''

    def __init__(
        self,
        options: Optional[PanTableOption] = None,
        data: str = '',
        ica: Optional[Ica] = None,
    ):
        '''
        these args are those passed from within yaml_filter
        '''
        self.options: PanTableOption = PanTableOption() if options is None else options
        self.data = data
        self.ica: Ica = Ica() if ica is None else ica

    @classmethod
    def from_yaml_filter(
        cls,
        options: Optional[dict] = None,
        data: str = '',
        element: Optional[CodeBlock] = None,
        doc: Optional[Doc] = None,
    ) -> PanCodeBlock:
        '''
        these args are those passed from within yaml_filter
        '''
        pan_table_options = PanTableOption() if options is None else PanTableOption.from_kwargs(**options)
        ica = Ica() if element is None else Ica(
            identifier=element.identifier,
            classes=[cls_ for cls_ in element.classes if cls_ != 'table'],
            attributes=element.attributes,
        )
        return cls(options=pan_table_options, data=data, ica=ica)

    def to_panflute_ast(self) -> CodeBlock:
        '''return a panflute AST representation

        TODO: handle differently if include exists and writable
        need to be able to configure pantable2csv on write location
        '''
        options_dict = self.options.kwargs
        data = self.data
        if options_dict:
            options_yaml = yaml.dump(options_dict, Dumper=get_yaml_dumper(), default_flow_style=False)
            if data:
                code_block = f'---\n{options_yaml}...\n{data}'
            else:
                code_block = f"---\n{options_yaml}"
        else:
            code_block = data
        classes = self.ica.classes
        if 'table' not in classes:
            # don't mutate it
            classes = ['table'] + classes
        return CodeBlock(
            code_block,
            identifier=self.ica.identifier,
            classes=classes,
            attributes=self.ica.attributes,
        )

    @classmethod
    def from_data_format(
        cls,
        data: np.ndarray[str],
        options: Optional[PanTableOption] = None,
        ica: Optional[Ica] = None,
    ) -> PanCodeBlock:
        '''construct from different data formats

        TODO: should io be done by PanCodeBLock.to_panflute_ast or other places?
        seems wrong to be here

        but it may actually belongs to here because where else for binary data?
        '''
        dump_func = {
            'csv': dump_csv_io,
        }
        options = PanTableOption() if options is None else options
        try:
            return cls(
                options=options,
                data=dump_func[options.format](data, options),
                ica=Ica() if ica is None else ica,
            )
        except KeyError:
            raise ValueError(f'Unspported format {options.format}.')

    def parse_options(
        self,
        shape: Tuple[int, int],
    ) -> Tuple[
        str,
        str,
        Spec,
        Align,
        Optional[np.ndarray[np.int64]],
        Optional[np.ndarray[np.int64]],
    ]:
        '''parsing PanTableOption to whatever PanTableStr.__init__ needed

        This is the point where correctness is checked most aggressively.
        Here we assumed the types are already correct, so we are checking
        things beyond types such as Optional, shape, positivity, etc.
        '''
        m, n = shape
        options = self.options
        options.normalize(shape=shape)

        short_caption = options.short_caption
        caption = options.caption

        # alignment, width
        spec = options.to_spec(n)
        # alignment_cells
        aligns = options.alignment_cells_to_align(shape)

        # ms
        _ms = options.ms
        ms: Optional[np.ndarray[np.int64]] = None if _ms is None else np.array(_ms, dtype=np.int64)

        # ns_head
        _ns_head = options.ns_head
        ns_head = None if _ns_head is None else np.array(_ns_head, dtype=np.int64)
        return short_caption, caption, spec, aligns, ms, ns_head

    @staticmethod
    def parse_data_str(str_array: np.ndarray[str]) -> np.ndarray[PanCell]:
        shape = str_array.shape
        m, n = shape
        cells_res = np.empty(shape, dtype='O')
        for i in range(m):
            for j in range(n):
                cells_res[i, j] = PanCell(str_array[i, j])
        return cells_res

    @staticmethod
    def parse_data_markdown(
        str_array: np.ndarray[str],
        fancy_table: bool = False,
        ica_cell_pat=re.compile(r'^(\([0-9, ]+\))?({[^{}]*})?$'),
        fancy_table_pat=re.compile(r'^({[^{}]*})?? ?(---|===|___)? ?({[^{}]*})?$'),
    ) -> Tuple[
        Optional[np.ndarray[np.int64]],
        Optional[np.ndarray[str]],
        np.ndarray[str],
        np.ndarray[str],
        np.ndarray[PanCell],
    ]:
        '''parse markdown in string array

        c.f. PanTableMarkdown.to_str_array
        '''
        m, n = str_array.shape
        offset = int(fancy_table)
        n -= offset

        shape = (m, n)
        icas: np.ndarray[str] = np.empty(shape, dtype='O')
        cells: np.ndarray[PanCell] = np.empty(shape, dtype='O')
        for i in range(m):
            for j in range(n):
                # protect already written PanCellBlock
                if cells[i, j] is None:
                    string = str_array[i, j + offset]
                    has_ica = False
                    idx_newline = string.find('\n')
                    # if newline
                    if idx_newline != -1:
                        ica_maybe = string[:idx_newline]
                        founds = ica_cell_pat.findall(ica_maybe)
                        if founds:
                            found = founds[0]
                            has_ica = True
                            ica_temp = found[1]
                            ica = f'[]{ica_temp}' if ica_temp else ''
                            shape_temp = found[0]
                            try:
                                shape = tuple(int(i.strip()) for i in shape_temp[1:-1].split(',')) if shape_temp else (1, 1)
                                if len(shape) != 2 or shape[0] <= 0 or shape[1] <= 0:
                                    print(f'Invalid cell shape {shape}, ignoring...', file=sys.stderr)
                                    has_ica = False
                                # TODO: get smarter to enlarge the box?
                                # Or expect a normalization later and modified PanCell.put to never write beyond boundary?
                                elif (shape[0] + i > m) or (shape[1] + j > n):
                                    print(f'The following cell overflow the table, ignoring the attributes: {string}', file=sys.stderr)
                                    has_ica = False
                            except ValueError:
                                print(f'Invalid cell shape {shape}, ignoring...', file=sys.stderr)
                                has_ica = False
                    if has_ica:
                        content = string[(idx_newline + 1):]
                    else:
                        ica = ''
                        shape = (1, 1)
                        content = string
                    icas[i, j] = ica
                    # since we already checked the cell is None, overwrite can default to True
                    PanCell.put(content, shape, (i, j), cells, overwrite=True)

        # ms, icas_rowblock, icas_row
        ms = None
        icas_rowblock: Optional[np.ndarray[str]] = None
        icas_row: np.ndarray[str] = np.full(m, '', dtype='O')
        if fancy_table:
            temp_markers = []
            temp_icas = []
            temp_idxs = []
            # icas_row
            for i in range(m):
                string = str_array[i, 0]
                if string.strip():
                    founds = fancy_table_pat.findall(string)
                    if founds:
                        found = founds[0]
                        # if has rowblock indicators
                        marker = found[1]
                        if marker:
                            temp_markers.append(marker)
                            temp_icas.append(found[0])
                            temp_idxs.append(i)
                        # * ignore the case that somone might put 2 attrs side-by-side
                        if (ica_row := found[2]):
                            icas_row[i] = f'[]{ica_row}'
                    else:
                        print(f'Cannot parse the fancy table cell {string}, ignroing...', file=sys.stderr)
            # only if markers found, determine ms, icas_rowblock
            if temp_idxs:
                temp_idxs = np.array(temp_idxs, dtype=np.int64)
                ms_excluding_empty_rowblocks = np.diff(temp_idxs + 1, prepend=0)
                size = ms_excluding_empty_rowblocks.size

                has_head = False
                has_foot = False
                i_start = 0
                i_end = size
                if temp_markers[0] == '===':
                    has_head = True
                    i_start = 1
                if size > 1 and temp_markers[-1] == '===':
                    has_foot = True
                    i_end = size - 1

                # put in a temporary structure first
                # because we don't know if body-head or body-body exists in each body
                body_list: List[Dict[str, Tuple[int, str]]] = []
                for i in range(i_start, i_end):
                    marker = temp_markers[i]
                    temp = (
                        ms_excluding_empty_rowblocks[i],
                        temp_icas[i],
                    )
                    # is_body_body
                    if marker == '___':
                        if body_list and 'body' not in (last_body := body_list[-1]):
                            last_body['body'] = temp
                        else:
                            body_list.append({'body': temp})
                    # is_body_head
                    elif marker == '---':
                        body_list.append({'head': temp})
                    else:
                        print(f'Cannot determine the following fancy-table row as head or foot, ignoring...: {str_array[temp_idxs[i], 0]}', file=sys.stderr)

                ms_list = []
                icas_rowblock_list = []
                if has_head:
                    ms_list.append(ms_excluding_empty_rowblocks[0])
                    ica = temp_icas[0]
                    icas_rowblock_list.append(f'[]{ica}' if ica else '')
                else:
                    ms_list.append(0)
                    icas_rowblock_list.append('')
                for body in body_list:
                    ica = ''
                    if 'head' in body:
                        m_, ica_ = body['head']
                        ms_list.append(m_)
                        if ica_:
                            ica = ica_
                    else:
                        ms_list.append(0)
                    # * ica of body-body will overwrite that of body-head
                    if 'body' in body:
                        m_, ica_ = body['body']
                        ms_list.append(m_)
                        if ica_:
                            ica = ica_
                    else:
                        ms_list.append(0)
                    icas_rowblock_list.append(f'[]{ica}' if ica else '')
                if has_foot:
                    i = size - 1
                    ms_list.append(ms_excluding_empty_rowblocks[i])
                    ica = temp_icas[i]
                    icas_rowblock_list.append(f'[]{ica}' if ica else '')
                else:
                    ms_list.append(0)
                    icas_rowblock_list.append('')
                ms = np.array(ms_list, dtype=np.int64)
                icas_rowblock = np.array(icas_rowblock_list, dtype='O')

        return ms, icas_rowblock, icas_row, icas, cells

    def to_pantablestr(self) -> PanTableStr:
        '''parse data and return a PanTableStr

        Exceptions might be raised here

        c.f. to_pancodeblock
        '''
        load_func = {
            'csv': load_csv_array,
        }
        options = self.options
        # c.f. PanTable(Str|Markdown).to_str_array
        try:
            str_array = load_func[options.format](self.data, options)
        except KeyError:
            raise ValueError(f'Unknown format: {options.format}')

        cls: Type[PanTableStr]
        ms: Optional[np.ndarray[np.int64]]
        icas_rowblock: Optional[np.ndarray[str]]
        icas_row: Optional[np.ndarray[str]]
        icas: Optional[np.ndarray[str]]
        if options.markdown:
            cls = PanTableMarkdown
            ms, icas_rowblock, icas_row, icas, cells = self.parse_data_markdown(str_array, fancy_table=options.fancy_table)
        else:
            cls = PanTableStr
            ms = None
            icas_rowblock = None
            icas_row = None
            icas = None
            cells = self.parse_data_str(str_array)

        short_caption, caption, spec, aligns, _ms, ns_head = self.parse_options(cells.shape)

        if ms is None:
            ms = _ms

        return cls(
            cells,
            self.ica,
            short_caption, caption,
            spec,
            ms, ns_head,
            icas_rowblock,
            icas_row,
            icas,
            aligns,
            options.table_width,
        )


# Table


@dataclass
class Ica:
    """a class of identifier, classes, and attributes"""
    identifier: str = ''
    classes: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)

    def to_panflute_ast(self) -> ListContainer[Plain]:
        '''to panflute AST element

        we choose a ListContainer-Plain-Span here as it is simplest to capture the Ica
        '''
        return ListContainer(Plain(Span(
            identifier=self.identifier,
            classes=self.classes,
            attributes=self.attributes,
        )))

    @classmethod
    def from_panflute_ast(cls, elem: ListContainer[Block]) -> Ica:
        if elem:
            try:
                span = elem[0].content[0]
                return cls(identifier=span.identifier, classes=span.classes, attributes=span.attributes)
            except AttributeError:
                print(f'Cannot parse element {elem}, setting to default', file=sys.stderr)
                return cls()
        else:
            return cls()


class FakeRepr:
    '''mixin for repr that doesn't yield itself after eval, from to_dict method
    '''

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return pformat(self.to_dict(), sort_dicts=False, compact=False, width=-1)

    def to_dict(self) -> dict:
        raise NotImplementedError


class Align:
    '''Alignment class
    '''

    ALIGN = np.array([
        "AlignDefault",
        "AlignLeft",
        "AlignRight",
        "AlignCenter",
    ])

    def __init__(self, aligns: np.ndarray[np.int8]):
        self.aligns = aligns

    def __repr__(self):
        return f'Align.from_aligns_text({self.aligns_text})'

    def __str__(self):
        return self.__repr__()

    @property
    def aligns_char(self):
        return self.aligns.view('S1')

    @property
    def aligns_idx(self) -> np.ndarray[np.int8]:
        '''
        this is designed such that aligns_text below works

        the last % 4 is to gunrantee garbage input still falls inside the idx range of ALIGN
        '''
        return (self.aligns - 3) % 11 % 6 % 4

    @property
    def aligns_text(self) -> np.ndarray[np.str_]:
        return self.ALIGN[self.aligns_idx]

    @property
    def aligns_string(self) -> str:
        '''the aligns string used in pantable codeblock

        such as LDRC...
        '''
        ndim = self.aligns.ndim
        if ndim == 2:
            n = self.aligns.shape[1]
            temp = self.aligns.astype(np.uint32).view(f'U{n}')
            return '\n'.join(np.ravel(temp))
        elif ndim == 1:
            n = self.aligns.size
            return self.aligns.view(f'S{n}')[0].decode()
        else:
            raise TypeError(f'The Align {self.aligns_char} has unexpected no. of dim.: {ndim}')

    @classmethod
    def from_aligns_char(cls, aligns_char: np.ndarray['S1']) -> Align:
        return cls(aligns_char.view(np.int8))

    @classmethod
    def from_aligns_text(cls, aligns_text: np.ndarray[Optional[str]]) -> Align:
        aligns_char = np.empty_like(aligns_text, dtype='S1')
        # ravel to handle arbitrary dimenions
        aligns_char_ravel = np.ravel(aligns_char)
        aligns_text_ravel = np.ravel(aligns_text)
        for i in range(aligns_text_ravel.size):
            align_text = aligns_text_ravel[i]
            aligns_char_ravel[i] = 'D' if align_text is None else align_text[5]
        return cls.from_aligns_char(aligns_char)

    @classmethod
    def default(cls, shape: Union[Tuple[int], Tuple[int, int]] = (1,)) -> Align:
        return cls(np.full(shape, 68, dtype=np.int8))


class Spec:
    '''a class of spec of PanTable
    '''

    def __init__(
        self,
        aligns: Align,
        col_widths: Optional[np.ndarray[np.float64]] = None,
    ):
        self.aligns = aligns
        self.col_widths: np.ndarray[np.float64] = np.full_like(aligns.aligns, np.nan, dtype=np.float64) if col_widths is None else col_widths

    def to_dict(self) -> dict:
        return {
            'aligns': self.aligns.aligns_text,
            'col_widths': self.col_widths,
        }

    def __repr__(self):
        return f'Spec({self.aligns.__repr__()}, {self.col_widths})'

    def __str__(self):
        return self.__repr__()

    @property
    def size(self) -> int:
        return self.aligns.aligns.size

    @classmethod
    def from_panflute_ast(cls, table: Table) -> Spec:
        spec = table.colspec

        n = len(spec)
        col_widths = np.empty(n, dtype=np.float64)

        try:
            aligns_list = []
            for i, (align, width) in enumerate(spec):
                aligns_list.append(align)
                col_widths[i] = np.nan if width == COLWIDTHDEFAULT else width
            aligns = Align.from_aligns_text(np.array(aligns_list))
        except ValueError:
            raise TypeError(f'pantable: cannot parse table spec {spec}')

        return cls(
            aligns,
            col_widths,
        )

    def to_panflute_ast(self) -> List[Tuple]:
        return [
            (align, COLWIDTHDEFAULT if np.isnan(width) else width)
            for align, width in zip(self.aligns.aligns_text, self.col_widths)
        ]

    @classmethod
    def default(cls, n_col: int = 1) -> Spec:
        return cls(Align.default((n_col,)))


class PanCell:
    '''a class of simple cell within PanTable

    We don't have a concept of standalone `PanCell`,
    they are always assumed to be within a `np.ndarray[PanCell]`.

    e.g. `is_at` is used to determine if PanCellBlock is at the canoncial
    location, and for `PanCell` it is always at canonical location.
    You cannot check if the current PanCell is really at a location in the grid.
    '''
    shape = (1, 1)
    idxs: Optional[Tuple[int, int]] = None

    def __init__(self, content: Union[ListContainer, str]):
        self.content = content

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'PanCell({repr(self.content)})'

    def is_at(self, loc: Tuple[int, int]) -> bool:
        '''return True if self is at canonical location'''
        return True

    @staticmethod
    def put(
        content: Union[ListContainer, str],
        shape: Tuple[int, int],
        idxs: Tuple[int, int],
        array: np.ndarray[PanCell],
        overwrite: bool = False,
    ):
        '''create a PanCell and put in array

        This is almost a class method but we don't
        return the created PanCell as it is already
        in the array, and the created PanCell does
        not necessary has the type of current class
        by the dispatch of PanCell/PanCellBock
        '''
        x, y = shape
        idx, idy = idxs
        if x == 1 and y == 1:
            cell = PanCell(content)
            array[idx, idy] = cell
        else:
            cell = PanCellBlock(content, shape, idxs)
            for i in range(idx, idx + x):
                for j in range(idy, idy + y):
                    if overwrite or array[i, j] is None:
                        array[i, j] = cell
                    else:
                        raise ValueError(f"At location {idxs} there's not enough empty cells for a block of size {shape} in the given array {array}")


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

    def is_at(self, loc: Tuple[int, int]) -> bool:
        '''return True if self is at canonical location'''
        return loc == self.idxs


class PanTableAbstract(ABC, FakeRepr):
    '''an abstract class of PanTables
    '''

    def __init__(
        self,
        cells: np.ndarray,
        ica_table: Ica,
        short_caption, caption,
        spec: Spec,
        ms: np.ndarray[np.int64], ns_head: np.ndarray[np.int64],
        icas_rowblock: np.ndarray,
        icas_row: np.ndarray,
        icas: np.ndarray,
        aligns: Align,
    ):
        self.cells = cells
        self.ica_table = ica_table
        self.short_caption = short_caption
        self.caption = caption
        self.spec = spec
        self._ms = ms
        self.ns_head = ns_head
        self.icas_rowblock = icas_rowblock
        self.icas_row = icas_row
        self.icas = icas
        self.aligns = aligns

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
        return {
            'cells': self.cells,
            'ica_table': self.ica_table,
            'short_caption': self.short_caption,
            'caption': self.caption,
            'spec': self.spec.to_dict(),
            'ms': self.ms,
            'ns_head': self.ns_head,
            'icas_rowblock': self.icas_rowblock,
            'icas_row': self.icas_row,
            'icas': self.icas,
            'aligns': self.aligns.aligns_text,
            # properties
            'shape': self.shape,
        }

    @abstractmethod
    def cells_stringified(self, width: int = 15, cannonical=True) -> np.ndarray[str]:
        '''return stringified cells

        :param int width: width per column
        '''
        return np.array([''])

    @property
    def m(self) -> int:
        return self._ms.sum()

    @property
    def n(self) -> int:
        return self.spec.size

    @property
    def shape(self) -> Tuple[int, int]:
        return (self.m, self.n)

    @property
    def m_bodies(self) -> int:
        return self.ns_head.size

    @property
    def m_icas_rowblock(self) -> int:
        '''
        only one ica per body
        '''
        return self.icas_rowblock.size

    @property
    def m_rowblocks(self) -> int:
        '''
        2 rowblocks per body
        '''
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
        del self.is_heads
        del self.is_foots
        del self.is_body_heads
        del self.is_body_bodies
        del self.body_idxs_row
        del self.icas_rowblock_idxs_row
        del self.rowblock_splitting_idxs
        del self.last_row_of_rowblock_idxs
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
    def icas_rowblock_idxs_row(self) -> np.ndarray[np.int64]:
        '''calculate the i-th row-block attrs that each row belongs to'''
        return (self.rowblock_idxs_row + 1) // 2

    @cached_property
    def rowblock_splitting_idxs(self) -> np.ndarray[np.int64]:
        '''applying np.split(array_of_rows, rowblock_splitting_idxs) would break it back into list of head, bodies, foot
        '''
        return np.cumsum(self._ms)[:-1]

    @cached_property
    def last_row_of_rowblock_idxs(self) -> Set[np.int64]:
        '''return a set of the indices of the last row per row-block excluding foot
        '''
        return set(np.cumsum(self._ms) - 1)

    def iter_rowblocks(self, array: np.ndarray) -> List[np.ndarray]:
        '''break array into list of head, bodies, foot

        assume array is iterables of rows
        '''
        return np.split(array, self.rowblock_splitting_idxs)

    def iterrows(self):
        '''
        TODO: this is not a good iterrows to work with
        '''
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
                'aligns': self.aligns.aligns_text[i],
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
        cells: np.ndarray[PanCell],
        ica_table: Optional[Ica] = None,
        short_caption: Optional[ListContainer[Inline]] = None, caption: Optional[ListContainer[Block]] = None,
        spec: Optional[Spec] = None,
        ms: Optional[np.ndarray[np.int64]] = None, ns_head: Optional[np.ndarray[np.int64]] = None,
        icas_rowblock: Optional[np.ndarray[Ica]] = None,
        icas_row: Optional[np.ndarray[Ica]] = None,
        icas: Optional[np.ndarray[Ica]] = None,
        aligns: Optional[Align] = None,
    ):
        self.cells = cells
        self.short_caption = short_caption
        self.caption: ListContainer[Block] = ListContainer() if caption is None else caption

        shape: Tuple[int, int] = cells.shape
        m, n = shape

        self.ica_table: Ica = Ica() if ica_table is None else ica_table
        self.spec: Spec = Spec.default(n) if spec is None else spec
        self.aligns: Align = Align.default(shape) if aligns is None else aligns

        # default to 1 row of TableHead and the rest is a single body of body
        self._ms: np.ndarray[np.int64] = np.array([1, 0, m - 1, 0], dtype=np.int64) if ms is None else ms

        m_bodies = (self._ms.size - 2) // 2
        self.ns_head: np.ndarray[np.int64] = np.zeros(m_bodies, dtype=np.int64) if ns_head is None else ns_head

        m_icas_rowblock = m_bodies + 2
        self.icas_rowblock: np.ndarray[Ica]
        if icas_rowblock is None:
            temp = np.empty(m_icas_rowblock, dtype='O')
            for i in range(m_icas_rowblock):
                temp[i] = Ica()
            self.icas_rowblock = temp
        else:
            self.icas_rowblock = icas_rowblock

        self.icas_row: np.ndarray[Ica]
        if icas_row is None:
            temp = np.empty(m, dtype='O')
            for i in range(m):
                temp[i] = Ica()
            self.icas_row = temp
        else:
            self.icas_row = icas_row

        self.icas: np.ndarray[Ica]
        if icas is None:
            temp = np.empty(shape, dtype='O')
            for i in range(m):
                for j in range(n):
                    temp[i, j] = Ica()
            self.icas = temp
        else:
            self.icas = icas

    def _repr_html_(self) -> str:
        try:
            return convert_text(self.to_panflute_ast(), input_format='panflute', output_format='html')
        # in case of an invalid panflute AST and still want to show something
        except Exception:
            return self.__str__(tablefmt='html')

    @staticmethod
    def iter_tablerows(
        icas_row: np.ndarray[Ica],
        pf_cells: np.ndarray[TableCell],
    ) -> Iterator[TableRow]:
        return (
            TableRow(
                *(i for i in pf_row_array if i is not None),
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
        aligns_flat = self.aligns.aligns_text.ravel()

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
        aligns_text = np.empty(shape, dtype='O')
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
                PanCell.put(cell.content, (cell.rowspan, cell.colspan), (i, j), cells)
                icas[i, j] = Ica(cell.identifier, cell.classes, cell.attributes)
                aligns_text[i, j] = cell.alignment
        return cls(
            cells,
            ica_table=ica_table,
            short_caption=short_caption, caption=caption,
            spec=spec,
            ms=ms, ns_head=ns_head,
            icas_rowblock=icas_rowblock,
            icas_row=icas_row,
            icas=icas,
            aligns=Align.from_aligns_text(aligns_text),
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

    def to_pantablemarkdown(self) -> PanTableMarkdown:
        '''return a PanTableMarkdown representation of self
        '''
        # * 1st pass: assemble the caches
        cache_elems: Dict[Union[str, Tuple[str, int], Tuple[str, int, int]], ListContainer] = {}
        # for holding the value as None cases
        cache_none: List[Union[str, Tuple[str, int, int]]] = []
        # caption
        cache_elems['caption'] = self.caption
        # short_caption
        short_caption = self.short_caption
        if short_caption is None:
            cache_none.append('short_caption')
        else:
            # iter_convert_texts_panflute_to_markdown accept ListContainer of Block only
            cache_elems['short_caption'] = ListContainer(Plain(*short_caption))
        # cells and icas
        m = self.m
        n = self.n
        cells = self.cells
        icas = self.icas
        for i in range(m):
            for j in range(n):
                cell = cells[i, j]
                # don't repeat PanCellBlock
                if cell.is_at((i, j)):
                    cache_elems[('cells', i, j)] = cell.content
                    cache_elems[('icas', i, j)] = icas[i, j].to_panflute_ast()
                else:
                    cache_none.append(('cells', i, j))
                    # don't need this below because checking is_at by cell only
                    # cache_none.append(('icas', i, j))
        # icas_row
        icas_row = self.icas_row
        for i in range(m):
            cache_elems[('icas_row', i)] = icas_row[i].to_panflute_ast()
        # icas_rowblock
        m_rowblocks = self.m_icas_rowblock
        icas_rowblock = self.icas_rowblock
        for i in range(m_rowblocks):
            cache_elems[('icas_rowblock', i)] = icas_rowblock[i].to_panflute_ast()

        # * batch convert to markdown
        # the bottle neck is calling pandoc so we batch them and call it once only
        cache_texts: Dict[Union[str, Tuple[str, int], Tuple[str, int, int]], Optional[str]] = {
            key: value
            for key, value in chain(
                zip(
                    cache_elems.keys(),
                    iter_convert_texts_panflute_to_markdown(cache_elems.values()),
                ),
                zip(cache_none, repeat(None))
            )
        }

        # * 2nd pass: get output from cache
        # cells and icas
        cells_res = np.empty((m, n), dtype='O')
        icas_res = np.empty((m, n), dtype='O')
        for i in range(m):
            for j in range(n):
                content = cache_texts[('cells', i, j)]
                if content is not None:
                    cell = cells[i, j]
                    # overwrite as cells is already valid so it is impossible to have
                    # colliding cells to be overwritten
                    PanCell.put(content, cell.shape, (i, j), cells_res, overwrite=True)
                    icas_res[i, j] = cache_texts[('icas', i, j)]
        # icas_row
        icas_row_res = np.empty(m, dtype='O')
        for i in range(m):
            icas_row_res[i] = cache_texts[('icas_row', i)]
        # icas_rowblock
        icas_rowblock_res = np.empty(m_rowblocks, dtype='O')
        for i in range(m_rowblocks):
            icas_rowblock_res[i] = cache_texts[('icas_rowblock', i)]

        return PanTableMarkdown(
            cells_res,
            ica_table=self.ica_table,
            short_caption=cache_texts['short_caption'], caption=cache_texts['caption'],
            spec=self.spec,
            ms=self._ms, ns_head=self.ns_head,
            icas_rowblock=icas_rowblock_res,
            icas_row=icas_row_res,
            icas=icas_res,
            aligns=self.aligns,
        )

    def to_pantablestr(self) -> PanTableStr:
        '''return a PanTableStr representation of self

        All contents are stringified so it is lossy.
        '''
        cells = self.cells
        shape = cells.shape
        m, n = shape
        cells_res = np.empty(shape, dtype='O')
        for i in range(m):
            for j in range(n):
                cell = cells[i, j]
                if cell.is_at((i, j)):
                    PanCell.put(stringify(TableCell(*cell.content)), cell.shape, (i, j), cells_res, overwrite=True)
        short_caption = None if self.short_caption is None else stringify(Plain(*self.short_caption))
        caption = stringify(Caption(*self.caption))
        return PanTableStr(
            cells_res,
            ica_table=self.ica_table,
            short_caption=short_caption, caption=caption,
            spec=self.spec,
            ms=self._ms, ns_head=self.ns_head,
            icas_rowblock=None,
            icas_row=None,
            icas=None,
            aligns=self.aligns,
        )


class PanTableStr(PanTableAbstract):
    '''similar to PanTable, but with panflute ASTs as str

    All PanCell in cells should have content type as str
    although not strictly enforced here

    TODO: check that icas* are always empty and remove them

    TODO: implement auto_width
    '''

    def __init__(
        self,
        cells: np.ndarray[PanCell],
        ica_table: Optional[Ica] = None,
        short_caption: Optional[str] = None, caption: str = '',
        spec: Optional[Spec] = None,
        ms: Optional[np.ndarray[np.int64]] = None, ns_head: Optional[np.ndarray[np.int64]] = None,
        icas_rowblock: Optional[np.ndarray[str]] = None,
        icas_row: Optional[np.ndarray[str]] = None,
        icas: Optional[np.ndarray[str]] = None,
        aligns: Optional[Align] = None,
        table_width: Optional[float] = None,
    ):
        self.cells = cells
        self.short_caption = short_caption
        self.caption = caption
        self.table_width = table_width

        shape = cells.shape
        m, n = shape

        self.ica_table: Ica = Ica() if ica_table is None else ica_table
        self.spec: Spec = Spec.default(n) if spec is None else spec
        self.aligns: Align = Align.default(shape) if aligns is None else aligns

        # default to 1 row of TableHead and the rest is a single body of body
        self._ms: np.ndarray[np.int64] = np.array([1, 0, m - 1, 0], dtype=np.int64) if ms is None else ms

        m_bodies = (self._ms.size - 2) // 2
        self.ns_head: np.ndarray[np.int64] = np.zeros(m_bodies, dtype=np.int64) if ns_head is None else ns_head

        m_icas_rowblock = m_bodies + 2
        self.icas_rowblock: np.ndarray[str] = np.full(m_icas_rowblock, '', dtype='O') if icas_rowblock is None else icas_rowblock
        self.icas_row: np.ndarray[str] = np.full(m, '', dtype='O') if icas_row is None else icas_row
        self.icas: np.ndarray[str] = np.full(shape, '', dtype='O') if icas is None else icas

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

    def to_pantableoption(
        self,
        format: str = 'csv',
        fancy_table: bool = False,
        include: str = '',
        csv_kwargs: Optional[dict] = None,
    ) -> PanTableOption:
        short_caption = self.short_caption
        spec = self.spec
        col_widths = spec.col_widths

        # col_width
        col_widths_list = ['D' if np.isnan(i) else float(i) for i in col_widths]

        options = PanTableOption(
            short_caption='' if short_caption is None else short_caption,
            caption=self.caption,
            alignment=spec.aligns.aligns_string,
            alignment_cells=self.aligns.aligns_string,
            width=col_widths_list,
            table_width=self.table_width,
            ms=self._ms.tolist(),
            ns_head=self.ns_head.tolist(),
            markdown=True,  # TODO: provide this as class attr and unify with stringify?
            fancy_table=fancy_table,
            include=include,
            csv_kwargs=dict() if csv_kwargs is None else csv_kwargs,
            format=format,
        )
        options.simplify()

        return options

    def to_pancodeblock(
        self,
        format: str = 'csv',
        fancy_table: bool = False,
        include: str = '',
        csv_kwargs: Optional[dict] = None,
    ) -> PanCodeBlock:
        return PanCodeBlock.from_data_format(
            self.to_str_array(fancy_table=fancy_table),
            options=self.to_pantableoption(format=format, fancy_table=fancy_table, include=include, csv_kwargs=csv_kwargs),
            ica=self.ica_table,
        )

    def to_pantable(self) -> PanTable:
        '''return a PanTable representation of self
        '''
        cells = self.cells
        shape = cells.shape
        m, n = shape
        cells_res = np.empty(shape, dtype='O')
        for i in range(m):
            for j in range(n):
                cell = cells[i, j]
                if cell.is_at((i, j)):
                    PanCell.put(ListContainer(Plain(Str(cell.content))), cell.shape, (i, j), cells_res, overwrite=True)
        short_caption = None if self.short_caption is None else ListContainer(Str(self.short_caption))
        caption = ListContainer(Para(Str(self.caption)))

        return PanTable(
            cells_res,
            ica_table=self.ica_table,
            short_caption=short_caption, caption=caption,
            spec=self.spec,
            ms=self._ms, ns_head=self.ns_head,
            icas_rowblock=None,
            icas_row=None,
            icas=None,
            aligns=self.aligns,
        )

    def to_str_array(self) -> np.ndarray[str]:
        cells = self.cells
        shape = cells.shape
        m, n = shape
        cells_res = np.full(shape, '', dtype='O')
        for i in range(m):
            for j in range(n):
                cell = cells[i, j]
                if cell.is_at((i, j)):
                    cells_res[i, j] = cell.content
        return cells_res


class PanTableMarkdown(PanTableStr):
    '''similar to PanTableStr, but with all str assumed to be in markdown
    '''

    def to_pantable(self) -> PanTable:
        '''return a PanTable representation of self
        '''
        # * 1st pass: assemble the caches
        cache_texts: Dict[Union[str, Tuple[str, int], Tuple[str, int, int]], str] = {}
        # for holding the value as None cases
        cache_none: List[Union[str, Tuple[str, int, int]]] = []
        # caption
        cache_texts['caption'] = self.caption
        # short_caption
        short_caption = self.short_caption
        if short_caption is None:
            cache_none.append('short_caption')
        else:
            cache_texts['short_caption'] = short_caption
        # cells and icas
        m = self.m
        n = self.n
        cells = self.cells
        icas = self.icas
        for i in range(m):
            for j in range(n):
                cell = cells[i, j]
                # don't repeat PanCellBlock
                if cell.is_at((i, j)):
                    cache_texts[('cells', i, j)] = cell.content
                    cache_texts[('icas', i, j)] = icas[i, j]
                else:
                    cache_none.append(('cells', i, j))
                    # don't need this below because checking is_at by cell only
                    # cache_none.append(('icas', i, j))
        # icas_row
        icas_row = self.icas_row
        for i in range(m):
            cache_texts[('icas_row', i)] = icas_row[i]
        # icas_rowblock
        m_rowblocks = self.m_icas_rowblock
        icas_rowblock = self.icas_rowblock
        for i in range(m_rowblocks):
            cache_texts[('icas_rowblock', i)] = icas_rowblock[i]

        # * batch convert to markdown
        # the bottle neck is calling pandoc so we batch them and call it once only
        cache_elems: Dict[Union[str, Tuple[str, int], Tuple[str, int, int]], Optional[ListContainer]] = {
            key: value
            for key, value in chain(
                zip(
                    cache_texts.keys(),
                    iter_convert_texts_markdown_to_panflute(cache_texts.values()),
                ),
                zip(cache_none, repeat(None))
            )
        }

        # * 2nd pass: get output from cache
        # short_caption
        temp = cache_elems['short_caption']
        short_caption_res = temp[0].content if temp else None
        # cells and icas
        cells_res = np.empty((m, n), dtype='O')
        icas_res = np.empty((m, n), dtype='O')
        for i in range(m):
            for j in range(n):
                content = cache_elems[('cells', i, j)]
                if content is not None:
                    cell = cells[i, j]
                    # overwrite as cells is already valid so it is impossible to have
                    # colliding cells to be overwritten
                    PanCell.put(single_para_to_plain(content), cell.shape, (i, j), cells_res, overwrite=True)
                    icas_res[i, j] = Ica.from_panflute_ast(cache_elems[('icas', i, j)])
        # icas_row
        icas_row_res = np.empty(m, dtype='O')
        for i in range(m):
            icas_row_res[i] = Ica.from_panflute_ast(cache_elems[('icas_row', i)])
        # icas_rowblock
        icas_rowblock_res = np.empty(m_rowblocks, dtype='O')
        for i in range(m_rowblocks):
            icas_rowblock_res[i] = Ica.from_panflute_ast(cache_elems[('icas_rowblock', i)])

        return PanTable(
            cells_res,
            ica_table=self.ica_table,
            short_caption=short_caption_res, caption=cache_elems['caption'],
            spec=self.spec,
            ms=self._ms, ns_head=self.ns_head,
            icas_rowblock=icas_rowblock_res,
            icas_row=icas_row_res,
            icas=icas_res,
            aligns=self.aligns,
        )

    def to_str_array(self, fancy_table: bool = False) -> np.ndarray[str]:
        '''construct a table with both content and ica together
        '''
        # prepend a column if fancy-table
        offset = int(fancy_table)
        m = self.m
        n = self.n

        res = np.full((m, n + offset), '', dtype='O')
        cells = self.cells
        icas = self.icas
        # cells, icas
        for i in range(m):
            for j in range(n):
                cell = cells[i, j]
                if cell.is_at((i, j)):
                    ica = icas[i, j]
                    cell_res = []
                    if type(cell) == PanCellBlock:
                        shape = cell.shape
                        cell_res.append(f'({shape[0]}, {shape[1]})')
                    if ica:
                        # discard first 2 char which is `[]`
                        cell_res.append(ica[2:])
                    # if cell_res has content so far that means we have first row for cell attributes
                    if cell_res:
                        cell_res.append('\n')
                    cell_res.append(cell.content)
                    res[i, j + offset] = ''.join(cell_res)
        # icas_rowblock, icas_row
        if fancy_table:
            icas_rowblock = self.icas_rowblock
            icas_row = self.icas_row

            icas_rowblock_idxs_row = self.icas_rowblock_idxs_row
            last_row_of_rowblock_idxs = self.last_row_of_rowblock_idxs
            is_heads = self.is_heads
            is_body_heads = self.is_body_heads
            is_body_bodies = self.is_body_bodies
            is_foots = self.is_foots
            for i in range(m):
                ica_row = icas_row[i]
                if i in last_row_of_rowblock_idxs:
                    temp_list = []
                    is_body_head = is_body_heads[i]
                    # * this is duplicated if within a body both body-head and body-body exists
                    ica_rowblock = icas_rowblock[icas_rowblock_idxs_row[i]]
                    if ica_rowblock:
                        temp_list.append(ica_rowblock[2:])
                    if is_body_bodies[i]:
                        temp_list.append('___')
                    elif is_body_head:
                        temp_list.append('---')
                    elif is_heads[i] or is_foots[i]:
                        temp_list.append('===')
                    if ica_row:
                        temp_list.append(ica_row[2:])
                    res[i, 0] = ' '.join(temp_list)
                else:
                    res[i, 0] = ica_row[2:]
        return res
