#!/usr/bin/env python3
"""
"""
from .context import parse_table_options


def test_parse_table_options():
    options = {
        'caption': None,
        'alignment': None,
        'width': None,
        'table-width': 1.0,
        'header': True,
        'markdown': True,
        'include': None
    }
    raw_table_list = [['1', '2', '3', '4'], ['5', '6', '7', '8']]
    # check init is preserved
    assert parse_table_options(
        options, raw_table_list) == options
    # check caption
    options['caption'] = '**sad**'
    assert str(parse_table_options(
        options, raw_table_list
    )['caption'][0]) == 'Strong(Str(sad))'
    # check alignment
    options['alignment'] = 'LRCD'
    assert parse_table_options(
        options, raw_table_list
    )['alignment'] == [
        'AlignLeft',
        'AlignRight',
        'AlignCenter',
        'AlignDefault'
    ]
    options['alignment'] = 'LRC'
    assert parse_table_options(
        options, raw_table_list
    )['alignment'] == [
        'AlignLeft',
        'AlignRight',
        'AlignCenter',
        'AlignDefault'
    ]
    # check width
    options['width'] = [0.1, 0.2, 0.3, 0.4]
    assert parse_table_options(
        options, raw_table_list
    )['width'] == [0.1, 0.2, 0.3, 0.4]
    # auto-width
    raw_table_list = [
        ['asdfdfdfguhfdhghfdgkla', '334\n2', '**la**', '4'],
        ['5', '6', '7', '8']
    ]
    options['width'] = None
    options['table-width'] = 1.2
    assert parse_table_options(
        options, raw_table_list
    )['width'] == [22 / 32 * 1.2, 3 / 32 * 1.2, 6 / 32 * 1.2, 1 / 32 * 1.2]
    return
