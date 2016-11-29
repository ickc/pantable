#!/usr/bin/env python3
"""
test panflute ast to markdown conversion
"""
from .context import get_table_options, parse_table_options, options2yaml
from panflute import *
import pickle


def test_getparse_table_options_options2yaml():
    with open('tests/grid_tables.pkl', 'rb') as file:
        doc = pickle.load(file)
    options = get_table_options(*doc.content)
    # test get_table_options
    assert options['caption']
    assert options['alignment']
    assert options['width']
    assert options['header']
    assert options['markdown'] is True
    # test parse_table_options
    parse_table_options(options)
    assert options['caption'] == '*abcd*'
    assert options['alignment'] == "LRCD"
    assert options['width'] == [0, 0, 0, 0]
    assert options['header'] is True
    assert options['markdown'] is True
    # test options2yaml
    options2yaml(options)
    assert options == {'alignment': 'LRCD', 'caption': '*abcd*', 'header': True, 'markdown': True, 'table-width': 0, 'width': [0, 0, 0, 0]}
    # parse_table_options without caption
    options = get_table_options(*doc.content)
    options['caption'] = ''
    parse_table_options(options)
    assert 'caption' not in options
    return
