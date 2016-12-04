"""
"""
from .context import get_width


def test_get_width():
    # check width
    # init
    options = {}
    assert get_width(options) is None
    # negative width
    options['width'] = [0.1, -0.2]
    assert get_width(options) is None
    # invalid width
    options['width'] = "happy"
    assert get_width(options) is None
    # invalid width 2
    options['width'] = ["happy", "birthday"]
    assert get_width(options) is None
    return
