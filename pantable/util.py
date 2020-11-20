import sys
from typing import List, Optional

import panflute
from panflute.tools import convert_text, run_pandoc


class PandocVersion:

    def __init__(self):
        version = run_pandoc(args=['--version'])
        self.version = version
        self.short_version = version.split('\n')[0].split(' ')[1]

    def __str__(self):
        return self.short_version

    def __repr__(self):
        return self.version


class EmptyTableError(Exception):
    pass


def ast_to_markdown(ast):
    """convert panflute AST to Markdown"""
    return panflute.convert_text(
        ast,
        input_format='panflute',
        output_format='markdown'
    )


def convert_texts(
    texts: List[str],
    input_format: str = 'markdown',
    output_format: str = 'panflute',
    standalone: bool = False,
    extra_args: Optional[List[str]] = None,
):
    '''run convert_text on list of text'''
    from functools import partial
    try:
        from map_parallel import map_parallel

        _map_parallel = partial(map_parallel, mode='multithreading')
    except ImportError:
        print(f'Consider `pip install map_parallel` to speed up `convert_texts`.', file=sys.stderr)
        _map_parallel = lambda f, arg: list(map(f, arg))

    _convert_text = partial(
        convert_text,
        input_format=input_format,
        output_format=output_format,
        standalone=standalone,
        extra_args=extra_args,
    )
    return _map_parallel(_convert_text, texts)


def convert_texts_fast(
    texts: List[str],
    extra_args: Optional[List[str]] = None,
):
    '''a faster, specialized convert_texts
    '''
    # TODO: generalize these as an option, e.g. add html?
    input_format: str = 'markdown'
    output_format: str = 'panflute'

    # put each text in a Div together
    text = '\n\n'.join(
        (
            f'''::: PanTableDiv :::
{text}
:::'''
            for text in texts
        )
    )
    pf = convert_text(text, input_format=input_format, output_format=output_format, extra_args=extra_args)
    return [list(elem.content) for elem in pf]


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

    doc = panflute.convert_text(text, standalone=True)
    return panflute.yaml_filter(doc.content[0], doc, tag='table', function=function, strict_yaml=True)


def table_for_pprint(table: panflute.Table):
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
