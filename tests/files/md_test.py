from pathlib import Path
import sys
from typing import Tuple

from pytest import mark

from panflute import convert_text
# use the function exactly used by the cli
from pantable.table_to_codeblock import table_to_codeblock

EXT = 'md'
PWD = Path(__file__).parent
DIRS = (PWD / 'md', PWD / 'md_reference')


def read(path: Path, path_ref: Path) -> Tuple[str, str]:
    '''test parsing table to codeblock
    '''
    print(f'Comparing {path} and {path_ref}...', file=sys.stderr)
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


@mark.parametrize('name', (path.stem for path in DIRS[0].glob(f'*.{EXT}')))
def test_md(name):
    paths = [dir_ / f'{name}.{EXT}' for dir_ in DIRS]
    res = read(*paths)
    assert res[0].strip() == res[1].strip()
