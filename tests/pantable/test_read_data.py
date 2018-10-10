"""
"""
#from .context import read_data


def test_read_data():
    # check include
    # invalid include: file doesn't exist
    assert read_data('abc.xyz', '') is None
    assert read_data('abc.xlsx', '') is None
    # invalid include: wrong type
    assert read_data(True, '') is None
    # valid include
    assert read_data('tests/csv_tables.csv', '') is not None
    assert read_data('tests/csv_tables.xlsx', '') is not None
    assert read_data('tests/csv_tables.xls', '') is not None
    # check type
    data = r"""1,2
3,4
"""
    assert read_data(None, data) == [
        ['1', '2'],
        ['3', '4']
    ]
    # check complex cells
    data = r"""asdfdfdfguhfdhghfdgkla,"334
2",**la**,4
5,6,7,8"""
    assert read_data(None, data) == [
        ['asdfdfdfguhfdhghfdgkla', '334\n2', '**la**', '4'],
        ['5', '6', '7', '8']
    ]
    # check include
    assert read_data('tests/csv_tables.csv',
                     data) == [['**_Fruit_**',
                                '~~Price~~',
                                '_Number_',
                                '`Advantages`'],
                               ['*Bananas~1~*',
                                '$1.34',
                                '12~units~',
                                'Benefits of eating bananas \n(**Note the appropriately\nrendered block markdown**):    \n\n- _built-in wrapper_        \n- ~~**bright color**~~\n\n'],
                               ['*Oranges~2~*',
                                '$2.10',
                                '5^10^~units~',
                                'Benefits of eating oranges:\n\n- **cures** scurvy\n- `tasty`']]
    assert read_data('tests/csv_tables.xlsx', 
                     data) == [['**_Fruit_**', '~~Price~~', '_Number_', '`Advantages`'],
                               ['*Bananas~1~*',
                                '1.34',
                                '12~units~',
                                'Benefits of eating bananas \r\n(**Note the appropriately\r\nrendered block markdown**):    \r\n\r\n- _built-in wrapper_        \r\n- ~~**bright color**~~\r\n\r\n'],
                               ['*Oranges~2~*',
                                '2.1',
                                '5^10^~units~',
                                'Benefits of eating oranges:\r\n\r\n- **cures** scurvy\r\n- `tasty`']]
    assert read_data('tests/csv_tables.xls',
                     data) == [['**_Fruit_**', '~~Price~~', '_Number_', '`Advantages`'],
                               ['*Bananas~1~*',
                                '1.34',
                                '12~units~',
                                'Benefits of eating bananas \r\n(**Note the appropriately\r\nrendered block markdown**):    \r\n\r\n- _built-in wrapper_        \r\n- ~~**bright color**~~\r\n\r\n'],
                               ['*Oranges~2~*',
                                '2.1',
                                '5^10^~units~',
                                'Benefits of eating oranges:\r\n\r\n- **cures** scurvy\r\n- `tasty`']]
    # check empty table
    assert read_data(None, '') == []
    return
