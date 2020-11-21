from pathlib import Path
import sys
from typing import Tuple

from panflute import convert_text
from pantable.util import parse_markdown_codeblock
# use the function exactly used by the cli
from pantable.cli.pantable import codeblock_to_table

EXT = 'md'
PWD = Path(__file__).parent
DIRS = (PWD / 'md_codeblock', PWD / 'md_codeblock_reference')


def gen_funcs():
    paths = list(Path(DIRS[0]).glob(f'*.{EXT}'))
    paths.sort()
    for path in paths:
        name = path.stem
        print(f'''def test_{name}():
    routine('{name}')''', end='\n\n\n')


def read(path: Path, path_ref: Path) -> Tuple[str, str]:
    '''test parsing markdown codeblock
    '''
    print(f'Comparing {path} and {path_ref}...', file=sys.stderr)
    with open(path, 'r') as f:
        text = f.read()
    with open(path_ref, 'r') as f:
        md_reference = f.read()

    try:
        kwargs = parse_markdown_codeblock(text)
        doc = codeblock_to_table(**kwargs)
        md_out = convert_text(doc, input_format='panflute', output_format='markdown')
    except TypeError:
        print(f'Cannot parse input codeblock, leaving as is.', file=sys.stderr)
        md_out = text

    return md_reference, md_out


def routine(name):
    paths = [dir_ / f'{name}.{EXT}' for dir_ in DIRS]
    res = read(*paths)
    assert res[0].strip() == res[1].strip()


# test_NAME will test against the file NAME.md
# use gen_funcs to generate the functions below
# python -c 'from tests.files.md_codeblock_test import gen_funcs as f; f()'


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


def test_invalid_yaml():
    routine('invalid_yaml')


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
