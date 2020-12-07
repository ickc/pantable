from pathlib import Path
import sys
from typing import Tuple

from panflute import convert_text
# use the function exactly used by the cli
from pantable.table_to_codeblock import table_to_codeblock

EXTs = ('native', 'md')
PWD = Path(__file__).parent
DIRS = (PWD / 'native', PWD / 'native_reference')


def gen_funcs():
    paths = list(Path(DIRS[0]).glob(f'*.{EXT[0]}'))
    paths.sort()
    for path in paths:
        name = path.stem
        print(f'''def test_{name}():
    routine('{name}')''', end='\n\n\n')


def read(path: Path, path_ref: Path) -> Tuple[str, str]:
    '''test parsing native to markdown codeblock with fancy-table
    '''
    print(f'Comparing {path} and {path_ref}...', file=sys.stderr)
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


def routine(name):
    paths = [dir_ / f'{name}.{ext}' for dir_, ext in zip(DIRS, EXTs)]
    res = read(*paths)
    assert res[0].strip() == res[1].strip()


# test_NAME will test against the file NAME.native
# use gen_funcs to generate the functions below
# python -c 'from tests.files.native_test import gen_funcs as f; f()'


def test_nordics():
    routine('nordics')


def test_planets():
    routine('planets')


def test_students():
    routine('students')
