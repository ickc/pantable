"""
"""
from .context import get_width


def test_get_width():
    # check width
    # init
    options = {}
    assert get_width(options, 2) is None
    # negative width
    options['width'] = [0.1, -0.2]
    assert get_width(options, 2) is None
    # invalid width
    options['width'] = "happy"
    assert get_width(options, 1) is None
    # invalid width 2
    options['width'] = ["happy", "birthday"]
    assert get_width(options, 2) is None
    # fractional
    options['width'] = ["1/2", "1/10"]
    assert get_width(options, 2) == [0.5, 0.1]
    # width too short
    options['width'] = [0.1, 0.2, 0.3]
    assert get_width(options, 4) is None
    # width too long
    options['width'] = [0.1, 0.2, 0.3, 0.4, 0.5]
    assert get_width(options, 4) is None
    return
