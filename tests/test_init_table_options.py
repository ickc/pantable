#!/usr/bin/env python3
"""

"""
from .context import pandoc_tables


def test_init_table_options():
    assert pandoc_tables.init_table_options({}) == {
        'caption': None,
        'alignment': None,
        'width': None,
        'table-width': 1.0,
        'header': True,
        'markdown': True,
        'include': None
    }
    return
