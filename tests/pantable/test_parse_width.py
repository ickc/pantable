"""
"""
from .context import parse_width


def test_parse_width():
    # init
    raw_table_list = [['1', '2', '3', '4'], ['5', '6', '7', '8']]
    assert parse_width([0.1, 0.2, 0.3, 0.4], 1.0, raw_table_list, 4) == [
        0.1, 0.2, 0.3, 0.4]
    # auto-width
    raw_table_list = [
        ['asdfdfdfguhfdhghfdgkla', '334\n2', '**la**', '4'],
        ['5', '6', '7', '8']
    ]
    assert parse_width(None, 1.2, raw_table_list, 4) == [25 / 44 * 1.2,
                                                         6 / 44 * 1.2, 9 / 44 * 1.2, 4 / 44 * 1.2]
    return
