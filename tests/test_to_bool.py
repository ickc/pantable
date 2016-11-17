#!/usr/bin/env python3
"""

"""
from .context import pandoc_tables


def test_to_bool():
    assert pandoc_tables.to_bool("true") == True
    assert pandoc_tables.to_bool("false") == False
    assert pandoc_tables.to_bool("yes") == True
    assert pandoc_tables.to_bool("no") == False
    assert pandoc_tables.to_bool("NO") == False
    return
