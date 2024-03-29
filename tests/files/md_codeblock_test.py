from logging import getLogger
from pathlib import Path
from typing import Tuple

from panflute import convert_text
from pytest import mark

# use the function exactly used by the cli
from pantable.codeblock_to_table import codeblock_to_table
from pantable.util import parse_markdown_codeblock

logger = getLogger('pantable')

EXT = 'md'
PWD = Path(__file__).parent
DIRS = (PWD / 'md_codeblock', PWD / 'md_codeblock_reference')


def read(path: Path, path_ref: Path) -> Tuple[str, str]:
    '''test parsing markdown codeblock
    '''
    logger.info(f'Comparing {path} and {path_ref}...')
    with open(path, 'r') as f:
        text = f.read()
    with open(path_ref, 'r') as f:
        md_reference = f.read()

    try:
        kwargs = parse_markdown_codeblock(text)
        doc = codeblock_to_table(**kwargs)
        md_out = convert_text(doc, input_format='panflute', output_format='markdown')
    except TypeError:
        logger.error('Cannot parse input codeblock, leaving as is.')
        md_out = text

    return md_reference, md_out


def read_io(name: str) -> Tuple[str, str]:
    paths = [dir_ / f'{name}.{EXT}' for dir_ in DIRS]
    return read(*paths)


@mark.parametrize('name', (path.stem for path in DIRS[0].glob(f'*.{EXT}')))
def test_md_codeblock(name):
    res = read_io(name)
    assert res[0].strip() == res[1].strip()
