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
            with open(path, 'r') as f:
                native = f.read()
            temp = convert_text(native, input_format='native')
            # input files should only have 1 single outter block
            assert len(temp) == 1
            table = temp[0]
            pan_table = PanTable.from_panflute_ast(table)
            table_idem = pan_table.to_panflute_ast()
            # check for idempotence
            native_orig = convert_text(table, input_format='panflute', output_format='native')
            native_idem = convert_text(table_idem, input_format='panflute', output_format='native')
            if native_orig == native_idem:
                print(f'{path} is identical after round trip.', file=sys.stderr)
            else:
                raise AssertionError(f'{path} is not identical after round trip.')
        except AssertionError as e:
            raise e
        except Exception as e:
            print(f'Cannot parse native file {path} into PanTable.', file=sys.stderr)
            raise e
