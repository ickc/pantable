"""
"""
from .context import get_include


def test_get_include():
    # check include
    # init
    options = {}
    assert get_include(options) is None
    # invalid include: file doesn't exist
    options['include'] = 'abc.xyz'
    assert get_include(options) is None
    # invalid include: wrong type
    options['include'] = True
    assert get_include(options) is None
    # valid include
    options['include'] = 'tests/csv_tables.csv'
    assert get_include(options) == 'tests/csv_tables.csv'
    return
