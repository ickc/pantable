#!/usr/bin/env python3
"""
`header` and `markdown` is checked by `test_to_bool` instead
"""
from .context import convert2table, main


def test_convert2table():
    data = r'''
1,2
3,4
'''
    table = convert2table({'width': [0, 0]}, data)
    assert str(table) == "Table(TableRow(TableCell(Plain(Str(1))) TableCell(Plain(Str(2)))) TableRow(TableCell(Plain(Str(3))) TableCell(Plain(Str(4)))); alignment=['AlignDefault', 'AlignDefault'], width=[0.0, 0.0], rows=2, cols=2)"
    return
