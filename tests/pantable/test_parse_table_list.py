"""

"""
from .context import parse_table_list


def test_parse_table_list():
    markdown = False
    raw_table_list = [['1', '2'], ['3', '4']]
    assert str(parse_table_list(markdown, raw_table_list)
               ) == '[TableRow(TableCell(Plain(Str(1))) TableCell(Plain(Str(2)))), TableRow(TableCell(Plain(Str(3))) TableCell(Plain(Str(4))))]'
    markdown = True
    raw_table_list = [['**markdown**', '~~like this~~'],
                      ['$E=mc^2$', '`great`']]
    assert str(parse_table_list(markdown, raw_table_list)
               ) == '''[TableRow(TableCell(Para(Strong(Str(markdown)))) TableCell(Para(Strikeout(Str(like) Space Str(this))))), TableRow(TableCell(Para(Math(E=mc^2; format='InlineMath'))) TableCell(Para(Code(great))))]'''
    # test irregular table
    markdown = True
    raw_table_list = [['1', '', '', '', '', ''],
                      ['2', '3', '4', '5', '6', '7']]
    assert str(parse_table_list(markdown, raw_table_list)
               ) == '''[TableRow(TableCell(Para(Str(1))) TableCell() TableCell() TableCell() TableCell() TableCell()), TableRow(TableCell(Para(Str(2))) TableCell(Para(Str(3))) TableCell(Para(Str(4))) TableCell(Para(Str(5))) TableCell(Para(Str(6))) TableCell(Para(Str(7))))]'''
    markdown = False
    assert str(
        parse_table_list(
            markdown,
            raw_table_list)) == '''[TableRow(TableCell(Plain(Str(1))) TableCell(Plain(Str())) TableCell(Plain(Str())) TableCell(Plain(Str())) TableCell(Plain(Str())) TableCell(Plain(Str()))), TableRow(TableCell(Plain(Str(2))) TableCell(Plain(Str(3))) TableCell(Plain(Str(4))) TableCell(Plain(Str(5))) TableCell(Plain(Str(6))) TableCell(Plain(Str(7))))]'''
    return
