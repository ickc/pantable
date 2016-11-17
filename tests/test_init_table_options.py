#!/usr/bin/env python3
"""

"""
from .context import init_table_options


def test_init_table_options():
    assert init_table_options({}) == {
        'caption': None,
        'alignment': None,
        'width': None,
        'table-width': 1.0,
        'header': True,
        'markdown': True,
        'include': None
    }
    return
