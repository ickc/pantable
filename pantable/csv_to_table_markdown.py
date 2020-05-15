import panflute

from .const import ALIGN_TO_IDXS, ALIGN_TO_PIPE_TABLE_DELIMITER
from .read_csv import parse_alignment, read_csv, regularize_table_list


def modified_align_border(text, alignment, header):
    '''Modify the alignment border row to include pandoc
    alignment syntax
    '''

    def modify_border(header_border, alignment):
        header_border = list(header_border)
        idxs = ALIGN_TO_IDXS[alignment]
        for idx in idxs:
            header_border[idx] = ':'
        return ''.join(header_border)

    text_list = text.split('\n')

    # walk to the header border
    if header:
        found = False
        for i, line in enumerate(text_list):
            if set(line) == {'+', '='}:
                found = True
                break
        if not found:
            panflute.debug('pantable: cannot add alignment to grid table.')
    else:
        i = 0

    # modify the line corresponding to the alignment border row
    header_border = text_list[i]

    header_border_list = header_border.split('+')[1:-1]

    header_border_list = [
        modify_border(header_border_i, alignment_i)
        for header_border_i, alignment_i in zip(header_border_list, alignment)
    ]

    text_list[i] = f"+{'+'.join(header_border_list)}+"

    return '\n'.join(text_list)


def csv_to_grid_tables(table_list, caption, alignment, header):
    try:
        import terminaltables
    except ImportError:
        panflute.debug('pantable: terminaltables not found. Please install by `pip install terminaltables`.')
        raise

    table = terminaltables.AsciiTable(table_list)
    table.inner_row_border = True
    if header:
        table.CHAR_H_INNER_HORIZONTAL = '='
    text = table.table

    if alignment:
        text = modified_align_border(text, alignment, header)
    if caption:
        text += f'\n\n: {caption}'
    return text


def csv_to_pipe_tables(table_list, caption, alignment):
    table_list.insert(1, [ALIGN_TO_PIPE_TABLE_DELIMITER[key] for key in alignment])
    pipe_table_list = ['|\t{}\t|'.format('\t|\t'.join(map(str, row))) for row in table_list]
    if caption:
        pipe_table_list.append('')
        pipe_table_list.append(f': {caption}')
    return '\n'.join(pipe_table_list)


def csv_to_table_markdown(options, data, use_grid_tables):
    """Construct pipe/grid table directly.
    """
    # prepare table in list from data/include
    table_list = read_csv(
        options.get('include', None),
        data,
        encoding=options.get('include-encoding', None),
        csv_kwargs=options.get('csv-kwargs', dict()),
    )

    # regularize table: all rows should have same length
    n_col = regularize_table_list(table_list)

    # parse alignment
    alignment = parse_alignment(options.get('alignment', None), n_col)
    del n_col
    # get caption
    caption = options.get('caption', None)

    text = csv_to_grid_tables(
        table_list, caption, alignment,
        (len(table_list) > 1 and options.get('header', True))
    ) if use_grid_tables else csv_to_pipe_tables(
        table_list, caption, alignment
    )

    raw_markdown = options.get('raw_markdown', False)
    if raw_markdown:
        return panflute.RawBlock(text, format='markdown')
    else:
        return panflute.convert_text(text)
