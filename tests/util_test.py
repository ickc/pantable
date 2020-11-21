from pantable.util import convert_texts, convert_texts_fast, eq_panflute_elems

texts_1 = [
    'some **markdown** here',
    'and ~~some~~ other?'
]

texts_2 = [
    'some *very* intersting markdown [example]{#so_fancy}',
    '''# Comical

Text

# Totally comical

Text'''
]

texts_3 = texts_1 + texts_2
elems_1 = convert_texts(texts_1)
elems_2 = convert_texts(texts_2)
elems_3 = convert_texts(texts_3)


def test_convert_texts_markdown_to_panflute_1():
    assert eq_panflute_elems(elems_1, convert_texts_fast(texts_1))


def test_convert_texts_markdown_to_panflute_2():
    assert eq_panflute_elems(elems_2, convert_texts_fast(texts_2))


def test_convert_texts_markdown_to_panflute_3():
    assert eq_panflute_elems(elems_3, convert_texts_fast(texts_3))


def test_convert_texts_panflute_to_markdown_1():
    assert texts_1 == convert_texts_fast(elems_1, input_format='panflute', output_format='markdown')


def test_convert_texts_panflute_to_markdown_2():
    assert texts_2 == convert_texts_fast(elems_2, input_format='panflute', output_format='markdown')


def test_convert_texts_panflute_to_markdown_3():
    assert texts_3 == convert_texts_fast(elems_3, input_format='panflute', output_format='markdown')
