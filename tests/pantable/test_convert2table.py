"""
`header` and `markdown` is checked by `test_to_bool` instead
"""
from .context import convert2table


def test_convert2table():
    # normal table
    data = r'''
1,2
3,4
'''
    table = convert2table({'width': [0, 0]}, data)
    assert str(
        table) == "Table(TableRow(TableCell(Plain(Str(1))) TableCell(Plain(Str(2)))) TableRow(TableCell(Plain(Str(3))) TableCell(Plain(Str(4)))); alignment=['AlignDefault', 'AlignDefault'], width=[0.0, 0.0], rows=2, cols=2)"
    # empty header_row
    table = convert2table({'header': False}, data)
    assert str(
        table) == "Table(TableRow(TableCell(Plain(Str())) TableCell(Plain(Str()))) TableRow(TableCell(Plain(Str(1))) TableCell(Plain(Str(2)))) TableRow(TableCell(Plain(Str(3))) TableCell(Plain(Str(4)))); alignment=['AlignDefault', 'AlignDefault'], width=[0.5, 0.5], rows=3, cols=2)"
    # empty table
    data = ','
    table = convert2table({}, data)
    assert table == []
    # 1 row table
    data = '1,2'
    table = convert2table({}, data)
    assert str(
        table) == r"""Table(TableRow(TableCell(Plain(Str(1))) TableCell(Plain(Str(2)))); alignment=['AlignDefault', 'AlignDefault'], width=[0.5, 0.5], rows=1, cols=2)"""
    # empty data
    table = convert2table({}, '')
    assert table == []
    return
