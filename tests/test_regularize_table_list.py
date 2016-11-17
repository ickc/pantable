#!/usr/bin/env python3
"""

"""
from .context import pandoc_tables


def test_regularize_table_list():
    raw_table_list = [['1'],['2','3','4','5','6','7']]
    assert pandoc_tables.regularize_table_list(raw_table_list) == [['1', '', '', '', '', ''], ['2', '3', '4', '5', '6', '7']]
    return
