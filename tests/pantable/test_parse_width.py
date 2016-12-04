"""
"""
from .context import parse_width


def test_parse_width():
    # init
    options = {}
    raw_table_list = [['1', '2', '3', '4'], ['5', '6', '7', '8']]
    options['width'] = [0.1, 0.2, 0.3, 0.4]
    assert parse_width(options, raw_table_list, 4) == [0.1, 0.2, 0.3, 0.4]
    # auto-width
    raw_table_list = [
        ['asdfdfdfguhfdhghfdgkla', '334\n2', '**la**', '4'],
        ['5', '6', '7', '8']
    ]
    options['width'] = None
    options['table-width'] = 1.2
    assert parse_width(options, raw_table_list, 4) == [22 / 32 * 1.2,
                                                       3 / 32 * 1.2, 6 / 32 * 1.2, 1 / 32 * 1.2]
    return
