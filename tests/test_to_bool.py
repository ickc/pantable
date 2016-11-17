#!/usr/bin/env python3
"""

"""
from .context import pandoc_tables


def test_to_bool():
    assert pandoc_tables.to_bool("true")
    assert pandoc_tables.to_bool("false") is False
    assert pandoc_tables.to_bool("yes")
    assert pandoc_tables.to_bool("no") is False
    assert pandoc_tables.to_bool("NO") is False
    return
