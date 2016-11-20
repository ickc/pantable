#!/usr/bin/env python3
"""
"""
from .context import init_table_options, parse_table_options


def test_parse_table_options():
    init_options = {}
    init_table_options(init_options)
    options = init_options.copy()
    raw_table_list = [['1', '2', '3', '4'], ['5', '6', '7', '8']]
    # check init is preserved
    parse_table_options(options, raw_table_list)
    assert options == options
    # check caption
    options['caption'] = '**sad**'
    parse_table_options(options, raw_table_list)
    assert str(options['caption'][0]) == 'Strong(Str(sad))'
    # check alignment
    options['alignment'] = 'LRC'
    parse_table_options(options, raw_table_list)
    assert options['alignment'] == [
        'AlignLeft',
        'AlignRight',
        'AlignCenter',
        'AlignDefault'
    ]
    # check width
    options['width'] = [0.1, 0.2, 0.3, 0.4]
    parse_table_options(options, raw_table_list)
    assert options['width'] == [0.1, 0.2, 0.3, 0.4]
    # auto-width
    raw_table_list = [
        ['asdfdfdfguhfdhghfdgkla', '334\n2', '**la**', '4'],
        ['5', '6', '7', '8']
    ]
    options['width'] = None
    options['table-width'] = 1.2
    parse_table_options(options, raw_table_list)
    assert options['width'] == [22 / 32 * 1.2, 3 / 32 * 1.2, 6 / 32 * 1.2, 1 / 32 * 1.2]
    return
