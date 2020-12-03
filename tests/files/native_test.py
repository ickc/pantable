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


def read(path: Path) -> Tuple[str, str, str, str]:
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
    # PanTableStr
    pan_table_markdown = pan_table.to_pantablemarkdown()
    pan_table_idem = pan_table_markdown.to_pantable()
    table_idem2 = pan_table_idem.to_panflute_ast()
    # PanCodeBlock
    pan_code_block = pan_table_markdown.to_pancodeblock(fancy_table=True)
    pan_table_markdown_idem = pan_code_block.to_pantablestr()
    # TODO
    pan_table_idem2 = pan_table_markdown_idem.to_pantable()
    table_idem3 = pan_table_idem2.to_panflute_ast()
    # TODO: for now just check it can convert
    pf_code_block = pan_code_block.to_panflute_ast()
    # check for idempotence
    native_orig = convert_text(table, input_format='panflute', output_format='native')
    native_idem = convert_text(table_idem, input_format='panflute', output_format='native')
    native_idem2 = convert_text(table_idem2, input_format='panflute', output_format='native')
    native_idem3 = convert_text(table_idem3, input_format='panflute', output_format='native')
    return native_orig, native_idem, native_idem2, native_idem3


def routine(name):
    path = DIR / f'{name}.{EXT}'
    res = read(path)
    # TODO
    assert res[0] == res[1] == res[2] == res[3]


# test_NAME will test against the file NAME.native
# use gen_funcs to generate the functions below
# python -c 'from tests.files.native_test import gen_funcs as f; f()'


def test_nordics():
    routine('nordics')


def test_planets():
    routine('planets')


def test_students():
    routine('students')
