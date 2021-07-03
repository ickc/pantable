from logging import getLogger
from pathlib import Path
from typing import Tuple

from panflute import convert_text
from pytest import mark

from pantable.ast import PanCodeBlock, PanTable
from pantable.util import parse_markdown_codeblock

logger = getLogger('pantable')

EXT = 'native'
DIR = Path(__file__).parent / EXT


def read(path: Path) -> Tuple[str, str, str, str, str]:
    '''test parsing native table into Pantable
    '''
    logger.info(f'Testing case {path}...')
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
    pan_codeblock = pan_table_markdown.to_pancodeblock(fancy_table=True)
    pan_table_markdown_idem = pan_codeblock.to_pantablestr()
    pan_table_idem2 = pan_table_markdown_idem.to_pantable()
    table_idem3 = pan_table_idem2.to_panflute_ast()
    # CodeBlock
    pf_codeblock = pan_codeblock.to_panflute_ast()
    md_codeblock = convert_text(pf_codeblock, input_format='panflute', output_format='markdown')
    kwargs = parse_markdown_codeblock(md_codeblock)
    pan_codeblock_idem = PanCodeBlock.from_yaml_filter(**kwargs)
    pan_table_markdown_idem2 = pan_codeblock_idem.to_pantablestr()
    pan_table_idem3 = pan_table_markdown_idem2.to_pantable()
    table_idem4 = pan_table_idem3.to_panflute_ast()
    # check for idempotence
    native_orig = convert_text(table, input_format='panflute', output_format='native')
    native_idem = convert_text(table_idem, input_format='panflute', output_format='native')
    native_idem2 = convert_text(table_idem2, input_format='panflute', output_format='native')
    native_idem3 = convert_text(table_idem3, input_format='panflute', output_format='native')
    native_idem4 = convert_text(table_idem4, input_format='panflute', output_format='native')
    return native_orig, native_idem, native_idem2, native_idem3, native_idem4


def read_io(name: str) -> Tuple[str, str, str, str, str]:
    path = DIR / f'{name}.{EXT}'
    return read(path)


@mark.parametrize('name', (path.stem for path in DIR.glob(f'*.{EXT}')))
def test_native_iden(name: str):
    res = read_io(name)
    assert res[0] == res[1]
    assert res[0] == res[2]
    assert res[0] == res[3]
    assert res[0] == res[4]
