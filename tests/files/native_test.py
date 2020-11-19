from pathlib import Path
import sys
import inspect
from typing import Tuple

from panflute import convert_text

from pantable.ast import PanTable

EXT = 'native'
DIR = Path(__file__).parent / EXT


def gen_funcs():
    paths = list(Path(DIR).glob(f'*.{EXT}'))
    paths.sort()
    for path in paths:
        print(f'''def test_{path.stem}():
    routine()''', end='\n\n\n')


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


def routine():
    # c.f. https://stackoverflow.com/a/5067654
    name = '_'.join(inspect.stack()[1][3].split('_')[1:])
    path = DIR / f'{name}.{EXT}'
    res = read(path)
    assert res[0] == res[1]

# test_NAME will test against the file NAME.native
# use gen_funcs to generate the functions below

def test_nordics():
    routine()


def test_planets():
    routine()


def test_students():
    routine()
