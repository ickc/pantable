"""
test pantable:

- `reference_pantable.native`: the correct output
- `test_pantable.native`: from `make`

test idempotency between pantable and pantable2csv:

- `reference_idempotent.native`: the 1st AST write
- `test_idempotent.native`: after AST-CSV-AST cycle
"""

import filecmp


def test_native():
    assert filecmp.cmp(
        'tests/reference_pantable.native',
        'tests/test_pantable.native'
    )
    assert filecmp.cmp(
        'tests/reference_idempotent.native',
        'tests/test_idempotent.native'
    )
    return
