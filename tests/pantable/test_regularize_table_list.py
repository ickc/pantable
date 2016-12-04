"""

"""
from .context import regularize_table_list


def test_regularize_table_list():
    raw_table_list = [['1'], ['2', '3', '4', '5', '6', '7']]
    regularize_table_list(raw_table_list)
    assert raw_table_list == [
        ['1', '', '', '', '', ''],
        ['2', '3', '4', '5', '6', '7']
    ]
    return
