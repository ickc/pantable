"""

"""
from .context import parse_table_list
from panflute import *


def test_parse_table_list():
    markdown = False
    raw_table_list = [['1', '2'], ['3', '4']]
    table_list_converted = parse_table_list(markdown, raw_table_list)
    table_list_referenced = [TableRow(TableCell(Plain(Str('1'))), TableCell(Plain(
        Str('2')))), TableRow(TableCell(Plain(Str('3'))), TableCell(Plain(Str('4'))))]
    assert repr(table_list_converted) == repr(table_list_referenced)
    markdown = True
    raw_table_list = [['**markdown**', '~~like this~~'],
                      ['$E=mc^2$', '`great`']]
    table_list_converted = parse_table_list(markdown, raw_table_list)
    table_list_referenced = [TableRow(TableCell(Para(Strong(Str('markdown')))), TableCell(Para(Strikeout(Str('like'), Space, Str(
        'this'))))), TableRow(TableCell(Para(Math('E=mc^2', format='InlineMath'))), TableCell(Para(Code('great'))))]
    assert repr(table_list_converted) == repr(table_list_referenced)
    # test irregular table
    markdown = True
    raw_table_list = [['1', '', '', '', '', ''],
                      ['2', '3', '4', '5', '6', '7']]
    table_list_converted = parse_table_list(markdown, raw_table_list)
    table_list_referenced = [TableRow(TableCell(Para(Str('1'))), TableCell(), TableCell(), TableCell(), TableCell(), TableCell()), TableRow(TableCell(
        Para(Str('2'))), TableCell(Para(Str('3'))), TableCell(Para(Str('4'))), TableCell(Para(Str('5'))), TableCell(Para(Str('6'))), TableCell(Para(Str('7'))))]
    assert repr(table_list_converted) == repr(table_list_referenced)
    markdown = False
    table_list_converted = parse_table_list(markdown, raw_table_list)
    table_list_referenced = [TableRow(TableCell(Plain(Str('1'))), TableCell(Plain(Str(''))), TableCell(Plain(Str(''))), TableCell(Plain(Str(''))), TableCell(Plain(Str(''))), TableCell(Plain(
        Str('')))), TableRow(TableCell(Plain(Str('2'))), TableCell(Plain(Str('3'))), TableCell(Plain(Str('4'))), TableCell(Plain(Str('5'))), TableCell(Plain(Str('6'))), TableCell(Plain(Str('7'))))]
    assert repr(table_list_converted) == repr(table_list_referenced)
    return
