"""
test panflute ast to markdown conversion
"""
from .context import table2csv
from panflute import *
import pickle


def test_table2csv():
    # get_table_body
    markdown = """| 1 | 2 | 3 | 4 |
|:--|--:|:-:|---|
| 1 | 2 | 3 | 4 |

: *abcd*
"""
    Panflute = convert_text(markdown)
    code_block = table2csv(*Panflute, {})
    assert str(code_block) == '''CodeBlock(---
alignment: LRCD
caption: '*abcd*'
header: true
markdown: true
table-width: 0
width: [0, 0, 0, 0]
---
1,2,3,4\r\n1,2,3,4\r\n; classes=['table'])'''
    return
