#!/usr/bin/env python3
"""
`header` and `markdown` is checked by `test_to_bool` instead
"""
from .context import init_table_options, check_table_options


def test_check_table_options():
    init_options = {}
    init_table_options(init_options)
    options = init_options.copy()
    # check init is preserved
    check_table_options(options)
    assert options == init_options
    # check width
    # negative width
    options['width'] = [0.1, -0.2]
    check_table_options(options)
    assert options['width'] == [0.1, 0]
    # invalid width
    options['width'] = "happy"
    check_table_options(options)
    assert options['width'] is None
    # invalid width 2
    options['width'] = ["happy", "birthday"]
    check_table_options(options)
    assert options['width'] is None
    # check table-width
    # negative table-width
    options['table-width'] = -1
    check_table_options(options)
    assert options['table-width'] == 1.0
    # invalid table-width
    options['table-width'] = "happy"
    check_table_options(options)
    assert options['table-width'] == 1.0
    # check include
    # invalid include: file doesn't exist
    options['include'] = 'abc.xyz'
    check_table_options(options)
    assert options['include'] is None
    # invalid include: wrong type
    options['include'] = True
    check_table_options(options)
    assert options['include'] is None
    # valid include
    options['include'] = 'tests/csv_tables.csv'
    check_table_options(options)
    assert options['include'] == 'tests/csv_tables.csv'
    return
