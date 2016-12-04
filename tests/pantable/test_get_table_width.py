"""
"""
from .context import get_table_width


def test_get_table_width():
    # check table-width
    # init
    options = {}
    assert get_table_width(options) == 1.0
    # negative table-width
    options['table-width'] = -1
    assert get_table_width(options) == 1.0
    # invalid table-width
    options['table-width'] = "happy"
    assert get_table_width(options) == 1.0
    return
