from logging import getLogger
from pathlib import Path
from typing import Tuple

from panflute import convert_text
from panflute.tools import pandoc_version
from pytest import mark, xfail

from pantable.ast import PanTable
# use the function exactly used by the cli
from pantable.table_to_codeblock import table_to_codeblock

logger = getLogger('pantable')

EXTs = ('native', 'md')
PWD = Path(__file__).parent
DIRS = (PWD / 'native', PWD / 'native_reference')


def read_table_to_codeblock(path: Path, path_ref: Path) -> Tuple[str, str]:
    '''test parsing native to markdown codeblock with fancy-table
    '''
    logger.info(f'Comparing {path} and {path_ref}...')
    with open(path, 'r') as f:
        text = f.read()
    with open(path_ref, 'r') as f:
        md_reference = f.read()

    doc = convert_text(text, input_format='native')
    # input files should only have 1 single outter block
    assert len(doc) == 1
    table = doc[0]
    doc_out = table_to_codeblock(table, doc, fancy_table=True)
    md_out = convert_text(doc_out, input_format='panflute', output_format='markdown')

    return md_reference, md_out


def read_table_to_codeblock_io(name: str) -> Tuple[str, str]:
    paths = [dir_ / f'{name}.{ext}' for dir_, ext in zip(DIRS, EXTs)]
    return read_table_to_codeblock(*paths)


@mark.parametrize('name', (path.stem for path in DIRS[0].glob(f'*.{EXTs[0]}')))
def test_table_to_codeblock(name: str):
    if pandoc_version.version < (2, 14) and name == 'planets':
        xfail("jgm/pandoc#7242 changed code-blocks output that is cosmetically different but semantically the same. Also see commit db7ce7d.")
    res = read_table_to_codeblock_io(name)
    assert res[0].strip() == res[1].strip()


def read_table_to_codeblock_not_fancy(path: Path):
    '''test parsing native to markdown codeblock without fancy-table

    This is lossy so we only check it runs
    '''
    logger.info(f'Loading {path}...')
    with open(path, 'r') as f:
        text = f.read()

    doc = convert_text(text, input_format='native')
    # input files should only have 1 single outter block
    assert len(doc) == 1
    table = doc[0]
    table_to_codeblock(table, doc, fancy_table=False)


@mark.parametrize('name', (path.stem for path in DIRS[0].glob(f'*.{EXTs[0]}')))
def test_table_to_codeblock_not_fancy(name):
    path = DIRS[0] / f'{name}.{EXTs[0]}'
    read_table_to_codeblock_not_fancy(path)


def read_table_to_codeblock_str(path: Path):
    '''test parsing native to markdown codeblock without markdown

    This is lossy so we only check it runs
    '''
    logger.info(f'Loading {path}...')
    with open(path, 'r') as f:
        text = f.read()

    doc = convert_text(text, input_format='native')
    # input files should only have 1 single outter block
    assert len(doc) == 1
    table = doc[0]
    pan_table = PanTable.from_panflute_ast(table)
    pan_table_str = pan_table.to_pantablestr()
    pan_table_str.to_pancodeblock()
    pan_table_str.to_pantable()


@mark.parametrize('name', (path.stem for path in DIRS[0].glob(f'*.{EXTs[0]}')))
def test_table_to_codeblock_str(name):
    path = DIRS[0] / f'{name}.{EXTs[0]}'
    read_table_to_codeblock_str(path)
