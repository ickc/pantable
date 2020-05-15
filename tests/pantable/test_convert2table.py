"""
`header` and `markdown` is checked by `test_to_bool` instead
"""
from panflute import *

from .context import codeblock_to_table


def test_codeblock_to_table():
    # normal table
    data = r'''
1,2
3,4
'''
    table_converted = codeblock_to_table({'width': [0, 0]}, data)
    table_referenced = Table(TableRow(TableCell(Plain(Str('1'))), TableCell(Plain(Str('2')))), TableRow(TableCell(
        Plain(Str('3'))), TableCell(Plain(Str('4')))), alignment=['AlignDefault', 'AlignDefault'], width=[0.0, 0.0])
    assert repr(table_converted) == repr(table_referenced)
    # empty header_row
    table_converted = codeblock_to_table({'header': False}, data)
    table_referenced = Table(TableRow(TableCell(Plain(Str(''))), TableCell(Plain(Str('')))), TableRow(TableCell(Plain(Str('1'))), TableCell(Plain(
        Str('2')))), TableRow(TableCell(Plain(Str('3'))), TableCell(Plain(Str('4')))), alignment=['AlignDefault', 'AlignDefault'], width=[0.5, 0.5])
    assert repr(table_converted) == repr(table_referenced)
    # empty table
    data = ','
    table = codeblock_to_table({}, data)
    assert table == []
    # 1 row table
    data = '1,2'
    table_converted = codeblock_to_table({}, data)
    table_referenced = Table(TableRow(TableCell(Plain(Str('1'))), TableCell(
        Plain(Str('2')))), alignment=['AlignDefault', 'AlignDefault'], width=[0.5, 0.5])
    assert repr(table_converted) == repr(table_referenced)
    # empty data
    table = codeblock_to_table({}, '')
    assert table == []
    return
