"""

"""
from .context import regularize_table_list


def test_regularize_table_list():
    table_list = [['1'], ['2', '3', '4', '5', '6', '7']]
    number_of_columns = regularize_table_list(table_list)
    assert table_list == [
        ['1', '', '', '', '', ''],
        ['2', '3', '4', '5', '6', '7']
    ]
    assert number_of_columns == 6
    return
