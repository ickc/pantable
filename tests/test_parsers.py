from pathlib import Path
import sys

from panflute import convert_text

from pantable.ast import PanTable


def test_from_panflute_ast():
    '''test parsing native table into Pantable
    '''
    paths = (Path(__file__).parent / 'native').glob('*.native')
    for path in paths:
        try:
            with open (path, 'r') as f:
                temp = convert_text(f.read(), input_format='native')
            # input files should only have 1 single outter block
            assert len(temp) == 1
            table = temp[0]
            pan_table = PanTable.from_panflute_ast(table)
        except Exception as e:
            print(f'Cannot parse native file {path} into PanTable.', file=sys.stderr)
            raise e
