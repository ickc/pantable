from pantable.ast import PanTableOption

default = PanTableOption()


def test_pantableoption_1():
    assert PanTableOption(table_width=3.) == PanTableOption(table_width=3)


def test_pantableoption_2():
    assert default == PanTableOption(table_width='string')


def test_pantableoption_3():
    assert default == PanTableOption(caption=2)


def test_pantableoption_4():
    assert default == PanTableOption(width=[1, 2, None])


def test_pantableoption_5():
    assert PanTableOption(width=[1, 2, '2/3']) == PanTableOption(width=[1, 2, 2 / 3])


def test_pantableoption_6():
    assert default == PanTableOption(csv_kwargs=[])


def test_pantableoption_7():
    assert PanTableOption(table_width='2/3') == PanTableOption(table_width=2 / 3)


def test_pantableoption_8():
    assert PanTableOption.from_kwargs(**{
        'caption': 'Some interesting...',
        'unknown-key': 'path towards error',
        'table-width': 0.5,
    }) == PanTableOption.from_kwargs(**{
        'caption': 'Some interesting...',
        'table-width': 0.5,
    })
