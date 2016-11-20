#!/usr/bin/env python3

"""
`reference_convert2table.native`: the correct output
`test_convert2table.native`: from `make`
"""

import filecmp


def test_native():
    assert filecmp.cmp(
        'tests/reference_convert2table.native',
        'tests/test_convert2table.native'
    )
    return
