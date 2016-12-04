"""
"""
from .context import parse_alignment


def test_parse_alignment():
    # init
    options = {}
    # check alignment
    options['alignment'] = 'LRC'
    assert parse_alignment(options, 4) == [
        'AlignLeft',
        'AlignRight',
        'AlignCenter',
        'AlignDefault'
    ]
    # check alignment too long
    options['alignment'] = 'LRCDLRCDLRCDLRCDLRCDLRCD'
    assert parse_alignment(options, 4) == [
        'AlignLeft',
        'AlignRight',
        'AlignCenter',
        'AlignDefault'
    ]
    # check invalid
    options['alignment'] = 'abcd'
    assert parse_alignment(options, 4) == [
        'AlignDefault',
        'AlignDefault',
        'AlignCenter',
        'AlignDefault'
    ]
    return
