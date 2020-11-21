import random
import string
import sys
from typing import List, Optional, Iterator
from functools import partial

from panflute.elements import ListContainer, Para, Str
from panflute.table_elements import Table
from panflute.tools import convert_text, run_pandoc, yaml_filter


class PandocVersion:
    '''get runtime pandoc verison

    use PandocVersion().version for comparing versions
    '''

    def __init__(self):
        self._repr = run_pandoc(args=['--version'])

    def __str__(self):
        return self._repr.split('\n')[0].split(' ')[1]

    def __repr__(self):
        return self._repr

    @property
    def version(self):
        return tuple(int(i) for i in str(self).split('.'))


class EmptyTableError(Exception):
    pass


def ast_to_markdown(ast):
    """convert panflute AST to Markdown"""
    return convert_text(
        ast,
        input_format='panflute',
        output_format='markdown'
    )


def convert_texts(
    texts: list,
    input_format: str = 'markdown',
    output_format: str = 'panflute',
    standalone: bool = False,
    extra_args: Optional[List[str]] = None,
) -> List[list]:
    '''run convert_text on list of text'''
    try:
        from map_parallel import map_parallel

        _map_parallel = partial(map_parallel, mode='multithreading')
    except ImportError:
        print('Consider `pip install map_parallel` to speed up `convert_texts`.', file=sys.stderr)

        def _map_parallel(f, arg):
            return list(map(f, arg))

    _convert_text = partial(
        convert_text,
        input_format=input_format,
        output_format=output_format,
        standalone=standalone,
        extra_args=extra_args,
    )
    return _map_parallel(_convert_text, texts)


def iter_convert_texts_markdown_to_panflute(
    texts: List[str],
    extra_args: Optional[List[str]] = None,
) -> Iterator[ListContainer]:
    '''a faster, specialized convert_texts
    '''
    # put each text in a Div together
    text = '\n\n'.join(
        (
            f'''::: PanTableDiv :::
{text}
:::'''
            for text in texts
        )
    )
    pf = convert_text(text, input_format='markdown', output_format='panflute', extra_args=extra_args)
    return (elem.content for elem in pf)


def iter_convert_texts_panflute_to_markdown(
    elems: List[ListContainer],
    extra_args: Optional[List[str]] = None,
    seperator: str = ''.join(random.choices(string.ascii_letters + string.digits, k=256)),
) -> Iterator[str]:
    '''a faster, specialized convert_texts

    :param list elems: must be list of ListContainer of Block. This is more restrictive than convert_texts
    :param str seperator: a string for seperator in the temporary markdown output
    '''
    def iter_seperator(elems: List[ListContainer], inserter: Para):
        '''insert between every element in a ListContainer'''
        for elem in elems:
            for i in elem:
                yield i
            yield inserter

    def iter_split_by_seperator(text: str, seperator: str) -> Iterator[str]:
        '''split the text into list by the seperator
        '''
        temp = []
        for line in text.split('\n'):
            if line != seperator:
                temp.append(line)
            else:
                res = '\n'.join(temp).strip()
                # reset for next yield
                temp = []
                yield res

    inserter = Para(Str(seperator))

    elems_inserted = ListContainer(*iter_seperator(elems, inserter))
    texts_converted = convert_text(elems_inserted, input_format='panflute', output_format='markdown')
    return iter_split_by_seperator(texts_converted, seperator)


convert_texts_func = {
    # this is just to convert returned value from
    # Iterator[ListContainer] to Iterator[list]
    # which is what convert_texts does
    ('markdown', 'panflute'): (
        lambda *args, **kwargs:
        map(list, iter_convert_texts_markdown_to_panflute(*args, **kwargs))
    ),
    ('panflute', 'markdown'): iter_convert_texts_panflute_to_markdown,
}


def convert_texts_fast(
    texts: list,
    input_format: str = 'markdown',
    output_format: str = 'panflute',
    extra_args: Optional[List[str]] = None,
) -> List[list]:
    '''a faster, specialized convert_texts

    should have identical result from convert_texts
    '''
    try:
        return list(
            convert_texts_func[
                (input_format, output_format)
            ](
                texts,
                extra_args=extra_args
            )
        )
    except KeyError:
        print(f'Unsupported input/output format pair: {input_format}, {output_format}. Doing it slowly...', file=sys.stderr)
        return convert_texts(
            texts,
            input_format,
            output_format,
            extra_args=extra_args,
        )


def eq_panflute_elem(elem1, elem2) -> bool:
    return repr(elem1) == repr(elem2)


def eq_panflute_elems(elems1: list, elems2: list) -> bool:
    if not len(elems1) == len(elems2):
        return False
    for elem1, elem2 in zip(elems1, elems2):
        if not eq_panflute_elem(elem1, elem2):
            return False
    return True


def parse_markdown_codeblock(text: str) -> dict:
    '''parse markdown CodeBlock just as `panflute.yaml_filter` would

    useful for development to obtain the objects that the filter
    would see after passed to `panflute.yaml_filter`

    :param str text: must be a single codeblock of class table in markdown
    '''

    def function(**kwargs):
        return kwargs

    doc = convert_text(text, standalone=True)
    return yaml_filter(doc.content[0], doc, tag='table', function=function, strict_yaml=True)


def table_for_pprint(table: Table):
    '''represent panflute Table in a dict structure for pprint

    >>> pprint(table_for_pprint(table), sort_dicts=False, compact=False, width=-1)

    Note:

    Each HeadRow, BodyRow, FootRow, Cell also has ica not shown here.

    TableBody has RowHeadColumns int
    '''
    return {
        'Table': (table.identifier, table.classes, table.attributes),
        'Caption': (tuple(short_caption) if (short_caption := table.caption.short_caption) else None, tuple(table.caption.content)),
        'specs': table.colspec,
        'TableHead': [list(row.content) for row in table.head.content],
        'TableBody': [list(row.content) for row in table.content[0].content],
        'TableFoot': [list(row.content) for row in table.foot.content],
    }


def get_first_type(cls):
    '''c.f. https://stackoverflow.com/a/50622643'''
    import typing

    def _find_type_origin(type_hint):
        if isinstance(type_hint, typing._SpecialForm):
            # case of typing.Any, typing.ClassVar, typing.Final, typing.Literal,
            # typing.NoReturn, typing.Optional, or typing.Union without parameters
            yield typing.Any
            return

        actual_type = typing.get_origin(type_hint) or type_hint  # requires Python 3.8
        if isinstance(actual_type, typing._SpecialForm):
            # case of typing.Union[…] or typing.ClassVar[…] or …
            for origins in map(_find_type_origin, typing.get_args(type_hint)):
                yield from origins
        else:
            yield actual_type

    hints = typing.get_type_hints(cls)

    # this one returns all types in a Union
    # return {
    #     name: [
    #         origin
    #         for origin in _find_type_origin(type_hint)
    #         if origin is not typing.Any
    #     ]
    #     for name, type_hint in hints.items()
    # }
    # only need the first one as I'm checking against Optional
    return {
        name: next(
            origin
            for origin in _find_type_origin(type_hint)
            if origin is not typing.Any
        )
        for name, type_hint in hints.items()
    }


def get_yaml_dumper():
    try:
        from yamlloader.ordereddict.dumpers import CSafeDumper as Dumper
    except ImportError:
        try:
            from yamlloader.ordereddict.dumpers import SafeDumper as Dumper
        except ImportError:
            print('Try `pip install yamlloader` or `conda install yamlloader -c conda-forge` to preserve yaml dict ordering.', file=sys.stderr)
            try:
                from yaml.cyaml import CSafeDumper as Dumper
            except ImportError:
                from yaml.dumper import SafeDumper as Dumper
    return Dumper
