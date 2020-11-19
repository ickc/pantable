from pathlib import Path
import sys
import inspect

from panflute import convert_text

from pantable.ast import PanTable


def routine():
    '''test parsing native table into Pantable
    '''
    # c.f. https://stackoverflow.com/a/5067654
    name = inspect.stack()[1][3].split('_')[1]

    path = Path(__file__).parent / 'native' / f'{name}.native'
    print(f'Testing case {name} in {path}...', file=sys.stderr)
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
    assert native_orig == native_idem

# test_NAME will test against the file NAME.native

def test_nordics():
    routine()


def test_planets():
    routine()


def test_students():
    routine()
