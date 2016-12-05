"""
"""
from .context import parse_width


def test_parse_width():
    raw_table_list = [
        ['asdfdfdfguhfdhghfdgkla', '334\n2', '**la**', '4'],
        ['5', '6', '7', '8']
    ]
    assert parse_width(1.2, 4, raw_table_list) == [25 / 44 * 1.2,
                                                         6 / 44 * 1.2, 9 / 44 * 1.2, 4 / 44 * 1.2]
    return
