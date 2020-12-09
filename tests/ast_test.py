import numpy as np

from pytest import mark

from pantable.ast import PanTableOption, Align


@mark.parametrize('kwargs1,kwargs2', (
    (
        {'table_width': 3.},
        {'table_width': 3},
    ),
    (
        {},
        {'table_width': 'string'},
    ),
    (
        {'caption': '2'},
        {'caption': 2},
    ),
    (
        {},
        {'csv_kwargs': []},
    ),
    (
        {'table_width': '2/3'},
        {'table_width': 2 / 3},
    ),
))
def test_pantableoption_type(kwargs1, kwargs2):
    assert PanTableOption(**kwargs1) == PanTableOption(**kwargs2)


@mark.parametrize('kwargs1,kwargs2,shape', (
    (
        {'width': [1, 2, 'D']},
        {'width': [1, 2, None]},
        (3, 3),
    ),
    (
        {'width': [1, 2, '2/3']},
        {'width': [1, 2, 2 / 3]},
        (3, 3),
    ),
))
def test_pantableoption_normalize(kwargs1, kwargs2, shape):
    op1 = PanTableOption(**kwargs1)
    op1.normalize(shape=shape)
    op2 = PanTableOption(**kwargs2)
    op2.normalize(shape=shape)
    assert op1 == op2



case_test = PanTableOption.from_kwargs(**{
    'caption': 'Some interesting...',
    'unknown-key': 'path towards error',
    'table-width': 0.5,
})


def test_pantableoption_unknown_key():
    assert case_test == PanTableOption.from_kwargs(**{
        'caption': 'Some interesting...',
        'table-width': 0.5,
    })


def test_pantableoption_kwargs():
    assert case_test == case_test.from_kwargs(**case_test.kwargs)


ALIGN_DICT = {
    'D': "AlignDefault",
    'L': "AlignLeft",
    'R': "AlignRight",
    'C': "AlignCenter",
}
aligns_char = ['D', 'R', 'C', 'L']


def test_align_text_1D():
    aligns_char_1D = np.array(aligns_char, dtype='S1')
    n = 4

    aligns = Align.from_aligns_char(aligns_char_1D)

    np.testing.assert_array_equal(aligns.aligns_char, aligns_char_1D)
    np.testing.assert_array_equal(aligns.aligns_idx, np.array([0, 2, 3, 1], dtype=np.int8))

    aligns_text = aligns.aligns_text
    for i in range(n):
        assert aligns_text[i] == ALIGN_DICT[aligns_char_1D[i].decode()]

    aligns_string = aligns.aligns_string
    assert aligns_string == 'DRCL'

    assert Align.from_aligns_text(aligns_text) == aligns
    print(Align.from_aligns_string(aligns_string).aligns, aligns.aligns)
    assert Align.from_aligns_string(aligns_string) == aligns


def test_align_text_2D():
    aligns_char_2D = np.array([aligns_char, list(reversed(aligns_char))], dtype='S1')
    m = 2
    n = 4

    aligns = Align.from_aligns_char(aligns_char_2D)

    np.testing.assert_array_equal(aligns.aligns_char, aligns_char_2D)
    np.testing.assert_array_equal(aligns.aligns_idx, np.array([
        [0, 2, 3, 1],
        [1, 3, 2, 0],
    ], dtype=np.int8))

    aligns_text = aligns.aligns_text
    for i in range(m):
        for j in range(n):
            assert aligns_text[i, j] == ALIGN_DICT[aligns_char_2D[i, j].decode()]

    aligns_string = aligns.aligns_string
    assert aligns_string == 'DRCL\nLCRD'

    assert Align.from_aligns_text(aligns_text) == aligns
    assert Align.from_aligns_string(aligns_string) == aligns
