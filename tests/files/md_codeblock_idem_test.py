from logging import getLogger
from pathlib import Path
from typing import Tuple

from panflute import convert_text
from pytest import mark

from pantable.ast import PanCodeBlock
from pantable.util import parse_markdown_codeblock

logger = getLogger('pantable')

EXT = 'md'
PWD = Path(__file__).parent
DIR = PWD / 'md_codeblock'


def round_trip(text: str) -> str:
    kwargs = parse_markdown_codeblock(text)
    pan_codeblock = PanCodeBlock.from_yaml_filter(**kwargs)
    doc = pan_codeblock.to_panflute_ast()
    return convert_text(doc, input_format='panflute', output_format='markdown')


def read(path: Path) -> Tuple[str, str, str]:
    '''test parsing markdown codeblock to PanCodeBlock
    '''
    logger.info(f'Testing idempotence with {path}...')
    with open(path, 'r') as f:
        text = f.read()

    text_out = round_trip(text)
    text_idem = round_trip(text_out)

    return text_out, text_idem, text


def read_io(name: str) -> Tuple[str, str, str]:
    path = DIR / f'{name}.{EXT}'
    return read(path)


@mark.parametrize('name', (path.stem for path in DIR.glob(f'*.{EXT}')))
def test_md_codeblock_idem(name):
    res = read_io(name)
    assert res[0].strip() == res[1].strip()
