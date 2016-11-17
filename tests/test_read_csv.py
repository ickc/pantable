#!/usr/bin/env python3
"""
"""
from .context import pandoc_tables
import panflute


def test_read_csv():
    include = None
    # check type
    data = r"""1,2
3,4
"""
    assert pandoc_tables.read_csv(include, data) == [
        ['1', '2'],
        ['3', '4']
    ]
    # check complex cells
    data = r"""asdfdfdfguhfdhghfdgkla,"334
2",**la**,4
5,6,7,8"""
    assert pandoc_tables.read_csv(include, data) == [
        ['asdfdfdfguhfdhghfdgkla', '334\n2', '**la**', '4'],
        ['5', '6', '7', '8']
    ]
    # check include
    include = 'tests/csv_tables.csv'
    assert pandoc_tables.read_csv(include,
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
    # check empty table
    include = None
    data = ''
    assert pandoc_tables.read_csv(include, data) == []
    return
