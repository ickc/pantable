from pantable.util import convert_texts, convert_texts_fast, eq_panflute_elems

from pytest import mark

# construct some texts cases
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

textss = [texts_1, texts_2, texts_1 + texts_2]

# reference answers
elemss = [convert_texts(texts) for texts in textss]


@mark.parametrize('elems,texts', zip(elemss, textss))
def test_convert_texts_markdown_to_panflute(elems, texts):
    assert eq_panflute_elems(elems, convert_texts_fast(texts))


@mark.parametrize('elems,texts', zip(elemss, textss))
def test_convert_texts_panflute_to_markdown(elems, texts):
    assert texts == convert_texts_fast(elems, input_format='panflute', output_format='markdown')
