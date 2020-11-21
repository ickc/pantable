from pathlib import Path
import sys
from typing import Tuple

from panflute import convert_text

from pantable.ast import PanTable

EXT = 'native'
DIR = Path(__file__).parent / EXT


def gen_funcs():
    paths = list(Path(DIR).glob(f'*.{EXT}'))
    paths.sort()
    for path in paths:
        name = path.stem
        print(f'''def test_{name}():
    routine('{name}')''', end='\n\n\n')


def read(path: Path) -> Tuple[str, str]:
    '''test parsing native table into Pantable
    '''
    print(f'Testing case {path}...', file=sys.stderr)
    with open(path, 'r') as f:
        native = f.read()
    doc = convert_text(native, input_format='native')
    # input files should only have 1 single outter block
    assert len(doc) == 1
    table = doc[0]
    pan_table = PanTable.from_panflute_ast(table)
    table_idem = pan_table.to_panflute_ast()
    # check for idempotence
    native_orig = convert_text(table, input_format='panflute', output_format='native')
    native_idem = convert_text(table_idem, input_format='panflute', output_format='native')
    return native_orig, native_idem


def routine(name):
    path = DIR / f'{name}.{EXT}'
    res = read(path)
    assert res[0] == res[1]


# test_NAME will test against the file NAME.native
# use gen_funcs to generate the functions below
# python -c 'from tests.files.native_test import gen_funcs as f; f()'


def test_nordics():
    routine('nordics')


def test_planets():
    routine('planets')


def test_students():
    routine('students')
