from pathlib import Path
import sys
from typing import Tuple

from panflute import convert_text
# use the function exactly used by the cli
from pantable.cli.pantable2csv import table_to_csv

EXT = 'md'
PWD = Path(__file__).parent
DIRS = (PWD / 'md', PWD / 'md_reference')


def gen_funcs():
    paths = list(Path(DIRS[0]).glob(f'*.{EXT}'))
    paths.sort()
    for path in paths:
        name = path.stem
        print(f'''def test_{name}():
    routine('{name}')''', end='\n\n\n')


def read(path: Path, path_ref: Path) -> Tuple[str, str]:
    '''test parsing table to codeblock
    '''
    print(f'Comparing {path} and {path_ref}...', file=sys.stderr)
    with open(path, 'r') as f:
        text = f.read()
    with open(path_ref, 'r') as f:
        md_reference = f.read()

    doc = convert_text(text, input_format='markdown')
    # input files should only have 1 single outter block
    assert len(doc) == 1
    table = doc[0]
    doc_out = table_to_csv(table, doc)
    md_out = convert_text(doc_out, input_format='panflute', output_format='markdown')

    return md_reference, md_out


def routine(name):
    paths = [dir_ / f'{name}.{EXT}' for dir_ in DIRS]
    res = read(*paths)
    assert res[0].strip() == res[1].strip()


# test_NAME will test against the file NAME.md
# use gen_funcs to generate the functions below
# python -c 'from tests.files.md_test import gen_funcs as f; f()'


def test_tables():
    routine('tables')
