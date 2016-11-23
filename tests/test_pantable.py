#!/usr/bin/env python3

"""
`reference_pantable.native`: the correct output
`test_pantable.native`: from `make`
"""

import filecmp


def test_native():
    assert filecmp.cmp(
        'tests/reference_pantable.native',
        'tests/test_pantable.native'
    )
    return
