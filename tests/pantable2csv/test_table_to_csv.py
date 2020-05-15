"""
test panflute ast to markdown conversion
"""
from panflute import CodeBlock, convert_text

from .context import table_to_csv


def test_table_to_csv():
    # get_table_body
    markdown = """| 1 | 2 | 3 | 4 |
|:--|--:|:-:|---|
| 1 | 2 | 3 | 4 |

: *abcd*
"""
    Panflute = convert_text(markdown)
    code_block_converted = table_to_csv(*Panflute, doc=None)
    code_block_referenced = CodeBlock('''---
alignment: LRCD
caption: '*abcd*'
header: true
markdown: true
table-width: 0
width:
- 0
- 0
- 0
- 0
---
1,2,3,4\r\n1,2,3,4\r\n''', classes=['table'])
    assert repr(code_block_converted) == repr(code_block_referenced)
    return
