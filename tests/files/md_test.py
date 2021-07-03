from logging import getLogger
from pathlib import Path
from typing import Tuple

from panflute import convert_text
from panflute.tools import pandoc_version
from pytest import mark, xfail

# use the function exactly used by the cli
from pantable.table_to_codeblock import table_to_codeblock

logger = getLogger('pantable')

EXT = 'md'
PWD = Path(__file__).parent
DIRS = (PWD / 'md', PWD / 'md_reference')


def read(path: Path, path_ref: Path) -> Tuple[str, str]:
    '''test parsing table to codeblock
    '''
    logger.info(f'Comparing {path} and {path_ref}...')
    with open(path, 'r') as f:
        text = f.read()
    with open(path_ref, 'r') as f:
        md_reference = f.read()

    doc = convert_text(text, input_format='markdown')
    # input files should only have 1 single outter block
    assert len(doc) == 1
    table = doc[0]
    doc_out = table_to_codeblock(table, doc)
    md_out = convert_text(doc_out, input_format='panflute', output_format='markdown')

    return md_reference, md_out


def read_io(name: str) -> Tuple[str, str]:
    paths = [dir_ / f'{name}.{EXT}' for dir_ in DIRS]
    return read(*paths)


@mark.parametrize('name', (path.stem for path in DIRS[0].glob(f'*.{EXT}')))
def test_md(name: str):
    if pandoc_version.version < (2, 14) and name == 'tables':
        xfail("jgm/pandoc#7242 changed code-blocks output that is cosmetically different but semantically the same. Also see commit db7ce7d.")
    res = read_io(name)
    assert res[0].strip() == res[1].strip()
