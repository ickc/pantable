import numpy as np

from pantable.ast import PanTableOption, Align

case_default = PanTableOption()
case_test = PanTableOption.from_kwargs(**{
    'caption': 'Some interesting...',
    'unknown-key': 'path towards error',
    'table-width': 0.5,
})

def test_pantableoption_type_1():
    assert PanTableOption(table_width=3.) == PanTableOption(table_width=3)


def test_pantableoption_type_2():
    assert case_default == PanTableOption(table_width='string')


def test_pantableoption_type_3():
    assert PanTableOption(caption='2') == PanTableOption(caption=2)


def test_pantableoption_type_4():
    assert case_default == PanTableOption(width=[1, 2, None])


def test_pantableoption_type_5():
    assert PanTableOption(width=[1, 2, '2/3']) == PanTableOption(width=[1, 2, 2 / 3])


def test_pantableoption_type_6():
    assert case_default == PanTableOption(csv_kwargs=[])


def test_pantableoption_type_7():
    assert PanTableOption(table_width='2/3') == PanTableOption(table_width=2 / 3)


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

    assert aligns.aligns_string == 'DRCL'

    np.testing.assert_array_equal(
        Align.from_aligns_text(aligns_text).aligns,
        aligns.aligns,
    )


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

    assert aligns.aligns_string == 'DRCL\nLCRD'

    np.testing.assert_array_equal(
        Align.from_aligns_text(aligns_text).aligns,
        aligns.aligns,
    )
