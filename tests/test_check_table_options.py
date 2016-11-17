#!/usr/bin/env python3
"""
`header` and `markdown` is checked by `test_to_bool` instead
"""
from .context import check_table_options


def test_check_table_options():
    options = {
        'caption': None,
        'alignment': None,
        'width': None,
        'table-width': 1.0,
        'header': True,
        'markdown': True,
        'include': None
    }
    # check init is preserved
    assert check_table_options(options) == options
    # check width
    # negative
    options['width'] = [0.1, -0.2]
    assert check_table_options(options)['width'] == [0.1, 0]
    # invalid
    options['width'] = "happy"
    assert check_table_options(options)['width'] is None
    # check table-width
    # negative
    options['table-width'] = -1
    assert check_table_options(options)['table-width'] == 1.0
    # invalid
    options['table-width'] = "happy"
    assert check_table_options(options)['table-width'] == 1.0
    # check include
    options['include'] = 'abc.xyz'
    assert check_table_options(options)['include'] is None
    options['include'] = 'tests/csv_tables.csv'
    assert (
        check_table_options(options)['include'] ==
        'tests/csv_tables.csv'
    )
    return
