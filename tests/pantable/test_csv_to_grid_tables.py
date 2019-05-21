"""
"""
from .context import csv_to_grid_tables


def test_csv_to_grid_tables():
    data = [['**_Fruit_**', '~~Price~~', '_Number_', '`Advantages`'],
            ['*Bananas~1~*',
             '$1.34',
             '12~units~',
             'Benefits of eating bananas\n(**Note the appropriately\nrendered block markdown**):\n\n- _built-in wrapper_\n- ~~**bright color**~~\n\n'],
            ['*Oranges~2~*',
             '$2.10',
             '5^10^~units~',
             'Benefits of eating oranges:\n\n- **cures** scurvy\n- `tasty`']]

    caption = 'Some *caption*.'
    alignment = ['AlignLeft', 'AlignCenter', 'AlignRight', 'AlignDefault']

    assert csv_to_grid_tables(data, caption, alignment, False) == '''+:-------------+:---------:+-------------:+-----------------------------+
| **_Fruit_**  | ~~Price~~ | _Number_     | `Advantages`                |
+--------------+-----------+--------------+-----------------------------+
| *Bananas~1~* | $1.34     | 12~units~    | Benefits of eating bananas  |
|              |           |              | (**Note the appropriately   |
|              |           |              | rendered block markdown**): |
|              |           |              |                             |
|              |           |              | - _built-in wrapper_        |
|              |           |              | - ~~**bright color**~~      |
|              |           |              |                             |
|              |           |              |                             |
+--------------+-----------+--------------+-----------------------------+
| *Oranges~2~* | $2.10     | 5^10^~units~ | Benefits of eating oranges: |
|              |           |              |                             |
|              |           |              | - **cures** scurvy          |
|              |           |              | - `tasty`                   |
+--------------+-----------+--------------+-----------------------------+

: Some *caption*.'''

    assert csv_to_grid_tables(data, caption, alignment, True) == '''+--------------+-----------+--------------+-----------------------------+
| **_Fruit_**  | ~~Price~~ | _Number_     | `Advantages`                |
+:=============+:=========:+=============:+=============================+
| *Bananas~1~* | $1.34     | 12~units~    | Benefits of eating bananas  |
|              |           |              | (**Note the appropriately   |
|              |           |              | rendered block markdown**): |
|              |           |              |                             |
|              |           |              | - _built-in wrapper_        |
|              |           |              | - ~~**bright color**~~      |
|              |           |              |                             |
|              |           |              |                             |
+--------------+-----------+--------------+-----------------------------+
| *Oranges~2~* | $2.10     | 5^10^~units~ | Benefits of eating oranges: |
|              |           |              |                             |
|              |           |              | - **cures** scurvy          |
|              |           |              | - `tasty`                   |
+--------------+-----------+--------------+-----------------------------+

: Some *caption*.'''
