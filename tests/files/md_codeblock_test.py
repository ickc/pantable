from pathlib import Path
import sys
import inspect
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
        print(f'''def test_{path.stem}():
        routine()''', end='\n\n\n')


def read(path: Path, path_ref: Path) -> Tuple[str, str]:
    '''test parsing markdown codeblock
    '''
    print(f'Comparing {path} and {path_ref}...', file=sys.stderr)
    with open(path, 'r') as f:
        text = f.read()
    with open(path_ref, 'r') as f:
        md_reference = f.read()

    kwargs = parse_markdown_codeblock(text)

    doc = codeblock_to_table(**kwargs)
    md_out = convert_text(doc, input_format='panflute', output_format='markdown')
    return md_reference, md_out


def routine():
    # c.f. https://stackoverflow.com/a/5067654
    name = '_'.join(inspect.stack()[1][3].split('_')[1:])
    paths = [dir_ / f'{name}.{EXT}' for dir_ in DIRS]
    res = read(*paths)
    assert res[0].strip() == res[1].strip()

# test_NAME will test against the file NAME.md
# use gen_funcs to generate the functions below

def test_comparison():
        routine()

def test_empty_csv():
        routine()

def test_encoding():
        routine()

def test_full_test():
        routine()

def test_grid_table():
        routine()
def test_include_external_csv():
        routine()


def test_include_external_csv_invalid_path():
        routine()


def test_invalid_yaml():
        routine()


def test_irregular_csv():
        routine()


def test_one_row_table():
        routine()


def test_pipe_table_1():
        routine()


def test_pipe_table_2():
        routine()


def test_simple_test():
        routine()


def test_testing_0_table_width():
        routine()


def test_testing_wrong_type():
        routine()
