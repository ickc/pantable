from pathlib import Path
import sys
import inspect
from typing import Tuple

from panflute import convert_text
from pantable.util import parse_markdown_codeblock
# use the function exactly used by the cli
from pantable.cli.pantable2csv import table_to_csv

EXT = 'md'
PWD = Path(__file__).parent
DIRS = (PWD / 'md', PWD / 'md_reference')


def gen_funcs():
    paths = list(Path(DIRS[0]).glob(f'*.{EXT}'))
    paths.sort()
    for path in paths:
        print(f'''def test_{path.stem}():
    routine()''', end='\n\n\n')


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


def routine():
    # c.f. https://stackoverflow.com/a/5067654
    name = '_'.join(inspect.stack()[1][3].split('_')[1:])
    paths = [dir_ / f'{name}.{EXT}' for dir_ in DIRS]
    res = read(*paths)
    assert res[0].strip() == res[1].strip()

# test_NAME will test against the file NAME.md
# use gen_funcs to generate the functions below

def test_tables():
    routine()
