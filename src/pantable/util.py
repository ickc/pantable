from __future__ import annotations

from functools import partial
from logging import getLogger
from typing import TYPE_CHECKING, Any, _SpecialForm, get_type_hints

from . import PY37

if not PY37:
    from typing import get_args, get_origin

import numpy as np
from panflute.elements import ListContainer, Para, Str
from panflute.tools import convert_text, run_pandoc, yaml_filter

if TYPE_CHECKING:
    from typing import Callable, Dict, Generator, Iterable, Iterator, List, Optional, Tuple

    from panflute.elements import Element

logger = getLogger('pantable')


class EmptyTableError(Exception):
    pass


def convert_texts(
    texts: Iterable,
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
        logger.warning('Consider `pip install map_parallel` to speed up `convert_texts`.')

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
    texts: Iterable[str],
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
    elems: Iterable[ListContainer],
    extra_args: Optional[List[str]] = None,
    seperator: str = np.random.randint(65, 91, size=256, dtype=np.uint8).view('S256')[0].decode(),
) -> Iterator[str]:
    '''a faster, specialized convert_texts

    :param list elems: must be list of ListContainer of Block.
        This is more restrictive than convert_texts which can also accept list of Block
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
        for line in text.splitlines():
            if line != seperator:
                temp.append(line)
            else:
                res = '\n'.join(temp).strip()
                # reset for next yield
                temp = []
                yield res

    inserter = Para(Str(seperator))

    elems_inserted = ListContainer(*iter_seperator(elems, inserter))
    # reference-location=block for footnotes, see issue #58
    texts_converted = convert_text(elems_inserted, input_format='panflute', output_format='markdown', extra_args=['--reference-location=block'])
    return iter_split_by_seperator(texts_converted, seperator)


convert_texts_func: Dict[Tuple[str, str], Callable[[Iterable, Optional[List[str]]], Iterator]] = {
    ('markdown', 'panflute'): (
        lambda *args, **kwargs:
        # this is just to convert returned value from
        # Iterator[ListContainer] to Iterator[list]
        # which is what convert_texts does
        map(list, iter_convert_texts_markdown_to_panflute(*args, **kwargs))
    ),
    ('panflute', 'markdown'): iter_convert_texts_panflute_to_markdown,
}


def convert_texts_fast(
    texts: Iterable,
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
                extra_args,
            )
        )
    except KeyError:
        logger.warning(f'Unsupported input/output format pair: {input_format}, {output_format}. Doing it slowly...')
        return convert_texts(
            texts,
            input_format,
            output_format,
            extra_args=extra_args,
        )


def eq_panflute_elem(elem1: Element, elem2: Element) -> bool:
    return repr(elem1) == repr(elem2)


def eq_panflute_elems(elems1: List[Element], elems2: List[Element]) -> bool:
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


if PY37:
    def _find_type_origin(type_hint: Any) -> Generator[Any, None, None]:
        if isinstance(type_hint, _SpecialForm):
            # case of Any, ClassVar, Final, Literal,
            # NoReturn, Optional, or Union without parameters
            yield Any
            return
        try:
            actual_type = type_hint.__origin__
        except AttributeError:
            # In case of non-typing types (such as <class 'int'>, for instance)
            actual_type = type_hint
        if isinstance(actual_type, _SpecialForm):
            # case of Union[…] or ClassVar[…] or …
            for origins in map(_find_type_origin, type_hint.__args__):
                yield from origins
        else:
            yield actual_type
else:
    def _find_type_origin(type_hint: Any) -> Generator[Any, None, None]:
        if isinstance(type_hint, _SpecialForm):
            # case of Any, ClassVar, Final, Literal,
            # NoReturn, Optional, or Union without parameters
            yield Any
            return
        actual_type = get_origin(type_hint) or type_hint
        if isinstance(actual_type, _SpecialForm):
            # case of Union[…] or ClassVar[…] or …
            for origins in map(_find_type_origin, get_args(type_hint)):
                yield from origins
        else:
            yield actual_type


def get_types(cls: Any) -> Dict[str, tuple]:
    '''returns all type hints in a Union

    c.f. https://stackoverflow.com/a/50622643
    '''
    return {
        name: tuple(
            origin
            for origin in _find_type_origin(type_hint)
            if origin is not Any
        )
        for name, type_hint in get_type_hints(cls).items()
    }


def get_yaml_dumper():
    try:
        from yamlloader.ordereddict.dumpers import CSafeDumper as Dumper
    except ImportError:
        try:
            from yamlloader.ordereddict.dumpers import SafeDumper as Dumper
        except ImportError:
            logger.warning('Try `pip install yamlloader` or `conda install yamlloader -c conda-forge` to preserve yaml dict ordering.')
            try:
                from yaml.cyaml import CSafeDumper as Dumper
            except ImportError:
                from yaml.dumper import SafeDumper as Dumper
    return Dumper
