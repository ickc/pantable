#!/usr/bin/env python3

"""
`csv_tables_test.native`: the correct output
`csv_tables.native`: from `make`
"""

import filecmp


def test_native():
    assert filecmp.cmp(
        'tests/csv_tables.native',
        'tests/csv_tables_test.native'
    )
    return
