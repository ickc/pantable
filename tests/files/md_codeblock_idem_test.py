from pathlib import Path
import sys
from typing import Tuple

from panflute import convert_text
from pantable.util import parse_markdown_codeblock
# use the function exactly used by the cli
from pantable.cli.pantable import codeblock_to_table
from pantable.ast import PanCodeBlock

EXT = 'md'
PWD = Path(__file__).parent
DIR = PWD / 'md_codeblock'


def gen_funcs():
    paths = list(Path(DIR).glob(f'*.{EXT}'))
    paths.sort()
    for path in paths:
        name = path.stem
        print(f'''def test_{name}():
    routine('{name}')''', end='\n\n\n')


def round_trip(text: str) -> str:
    kwargs = parse_markdown_codeblock(text)
    pan_codeblock = PanCodeBlock(**kwargs)
    doc = pan_codeblock.to_panflute_ast()
    return convert_text(doc, input_format='panflute', output_format='markdown')


def read(path: Path) -> Tuple[str, str, str]:
    '''test parsing markdown codeblock to PanCodeBlock
    '''
    print(f'Testing idempotence with {path}...', file=sys.stderr)
    with open(path, 'r') as f:
        text = f.read()

    text_out = round_trip(text)
    text_idem = round_trip(text_out)

    return text_out, text_idem, text


def routine(name):
    path = DIR / f'{name}.{EXT}'
    res = read(path)
    assert res[0].strip() == res[1].strip()


def read_all():
    '''run `read` on all test cases for manual debugging
    '''
    return (read(path) for path in Path(DIR).glob(f'*.{EXT}') if path.stem != 'invalid_yaml')


def print_all():
    for text_out, text_idem, text in read_all():
        assert text_out == text_idem
        print(text, text_out, sep='\n' + '-' * 80 + '\n', end='\n' + '=' * 80 + '\n')


# test_NAME will test against the file NAME.md
# use gen_funcs to generate the functions below
# python -c 'from tests.files.md_codeblock_idem_test import gen_funcs as f; f()'


def test_comparison():
    routine('comparison')


def test_empty_csv():
    routine('empty_csv')


def test_encoding():
    routine('encoding')


def test_full_test():
    routine('full_test')


def test_grid_table():
    routine('grid_table')


def test_include_external_csv():
    routine('include_external_csv')


def test_include_external_csv_invalid_path():
    routine('include_external_csv_invalid_path')


# invalid YAML is handled by panflute, not us
# def test_invalid_yaml():
#     routine('invalid_yaml')


def test_irregular_csv():
    routine('irregular_csv')


def test_one_row_table():
    routine('one_row_table')


def test_pipe_table_1():
    routine('pipe_table_1')


def test_pipe_table_2():
    routine('pipe_table_2')


def test_simple_test():
    routine('simple_test')


def test_testing_0_table_width():
    routine('testing_0_table_width')


def test_testing_wrong_type():
    routine('testing_wrong_type')
