"""
"""
from .context import csv_to_pipe_tables


def test_csv_to_pipe_tables():
    table_list = [
        [1, 2, 3, 4],
        [4, 5, 6, 7]
    ]
    caption = 'Some *caption*.'

    alignment = ['AlignLeft', 'AlignCenter', 'AlignRight', 'AlignDefault']

    text = csv_to_pipe_tables(table_list, caption, alignment)
    assert text == '''|	1	|	2	|	3	|	4	|
|	:---	|	:---:	|	---:	|	---	|
|	4	|	5	|	6	|	7	|

: Some *caption*.'''