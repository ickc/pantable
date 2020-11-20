from pantable.util import convert_texts, convert_texts_fast, eq_panflute_elems


def test_convert_texts():
    texts = [
        'some **markdown** here',
        'and ~~some~~ other?'
    ]
    assert eq_panflute_elems(convert_texts(texts), convert_texts_fast(texts))
