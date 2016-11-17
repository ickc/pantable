#!/usr/bin/env python3

"""
`test_convert2table_reference.native`: the correct output
`test_convert2table.native`: from `make`
"""

import filecmp


def test_native():
    assert filecmp.cmp(
        'tests/test_convert2table_reference.native',
        'tests/test_convert2table.native'
    )
    return
