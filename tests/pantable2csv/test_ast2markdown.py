#!/usr/bin/env python3
"""
test panflute ast to markdown conversion
"""
from .context import ast2markdown
from panflute import *


def test_ast2markdown():
    md = 'Some *markdown* **text** ~xyz~'
    md2ast = convert_text(md)
    assert ast2markdown(*md2ast) == md
    return
