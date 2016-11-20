#!/usr/bin/env python3
"""

"""
from .context import init_table_options


def test_init_table_options():
    init_options = {
        'caption': None,
        'alignment': None,
        'width': None,
        'table-width': 1.0,
        'header': True,
        'markdown': False,
        'include': None
    }
    options = {}
    init_table_options(options)
    assert options == init_options
    return
