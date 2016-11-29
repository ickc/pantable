#!/usr/bin/env python3
"""
test panflute ast to markdown conversion
"""
from .context import get_table_body, Table2list, list2csv
from panflute import *
import pickle


def test_get_table_body_Table2list_list2csv():
    # get_table_body
    with open('tests/grid_tables.pkl', 'rb') as file:
        doc = pickle.load(file)
    elem = doc.content[0]
    table_body = get_table_body({'header': True}, elem)
    assert table_body[0] == elem.header
    # Table2list
    table_list = Table2list(table_body)
    assert table_list == [['1', '2', '3', '4'], ['1', '2', '3', '4']]
    # list2csv
    csv_table = list2csv(table_list)
    assert csv_table == '1,2,3,4\r\n1,2,3,4\r\n'
    return
