from pantable.ast import PanTableOption

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
    assert case_default == PanTableOption(caption=2)


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
