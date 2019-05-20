#!/usr/bin/env python

r"""Panflute filter to parse CSV table in fenced YAML code blocks."""

import csv
import fractions
import io

import panflute


def get_width(options, n_col):
    """parse `options['width']` if it is list of non-negative numbers
    else return None.
    """
    if 'width' not in options:
        return

    width = options['width']

    if len(width) != n_col:
        panflute.debug("pantable: given widths different from no. of columns in the table.")
        return

    try:
        width = [float(fractions.Fraction(x)) for x in width]
    except ValueError:
        panflute.debug("pantable: specified width is not valid number or fraction and is ignored.")
        return

    for width_i in width:
        if width_i < 0.:
            panflute.debug("pantable: width cannot be negative.")
            return

    return width


def get_table_width(options):
    """parse `options['table-width']` if it is positive number
    else return 1.
    """
    if 'table-width' not in options:
        return 1.

    table_width = options['table-width']

    try:
        table_width = float(fractions.Fraction(table_width))
    except ValueError:
        panflute.debug("pantable: table width should be a number or fraction. Set to 1 instead.")
        return 1.

    if table_width <= 0.:
        panflute.debug("pantable: table width must be positive. Set to 1 instead.")
        return 1.

    return table_width


def auto_width(table_width, n_col, table_list):
    """Calculate width automatically according to length of cells.
    Return None if table is empty.
    """
    # calculate max line width per column
    max_col_width = [
        max(
            max(map(len, row[j].split("\n")))
            for row in table_list
        )
        for j in range(n_col)
    ]

    width_tot = sum(max_col_width)

    if width_tot == 0:
        panflute.debug("pantable: table is empty.")
        return

    # The +3 match the way pandoc handle width, see jgm/pandoc commit 0dfceda
    scale = table_width / (width_tot + 3 * n_col)
    return [(width + 3) * scale for width in max_col_width]


def parse_alignment(alignment_string, n_col):
    """
    `alignment` string is parsed into pandoc format (AlignDefault, etc.).
    Cases are checked:

    - if not given, return None (let panflute handle it)
    - if wrong type
    - if too long
    - if invalid characters are given
    - if too short
    """
    align_dict = {
        'l': "AlignLeft",
        'c': "AlignCenter",
        'r': "AlignRight",
        'd': "AlignDefault"
    }

    def get(key):
        '''parsing alignment'''
        key_lower = key.lower()
        if key_lower not in align_dict:
            panflute.debug("pantable: alignment: invalid character {} found, replaced by the default 'd'.".format(key))
            key_lower = 'd'
        return align_dict[key_lower]

    # alignment string can be None or empty; return None: set to default by
    # panflute
    if not alignment_string:
        return

    # test valid type
    if not isinstance(alignment_string, str):
        panflute.debug("pantable: alignment should be a string. Set to default instead.")
        # return None: set to default by panflute
        return

    n = len(alignment_string)

    if n > n_col:
        alignment_string = alignment_string[:n_col]
        panflute.debug("pantable: alignment string is too long, truncated.")

    alignment = [get(key) for key in alignment_string]

    # fill up with default if too short
    if n < n_col:
        alignment += ["AlignDefault"] * (n_col - n)

    return alignment


def read_data(include, data):
    """Parse CSV table.

    `include`: path to CSV file or None. This is prioritized first.

    `data`: str of CSV table.

    Return None when the include path is invalid.
    """
    try:
        with (io.StringIO(data) if include is None else io.open(str(include))) as f:
            raw_table_list = list(csv.reader(f))
    except FileNotFoundError:
        panflute.debug("pantable: file not found from the path {}. Leaving as is.".format(include))
        return

    return raw_table_list


def regularize_table_list(raw_table_list):
    """When the length of rows are uneven, make it as long as the longest row.

    `raw_table_list` modified inplace.

    return `n_col`
    """
    length_of_rows = [len(row) for row in raw_table_list]
    n_col = max(length_of_rows)

    for i, (n, row) in enumerate(zip(length_of_rows, raw_table_list)):
        if n != n_col:
            row += [''] * (n_col - n)
            panflute.debug("pantable: the {}-th row is shorter than the longest row. Empty cells appended.")
    return n_col


def parse_table_list(markdown, table_list):
    """read table in list and return panflute table format
    """

    def markdown_to_table_cell(string):
        return panflute.TableCell(*panflute.convert_text(string))

    def plain_to_table_cell(string):
        return panflute.TableCell(panflute.Plain(panflute.Str(string)))

    to_table_cell = markdown_to_table_cell if markdown else plain_to_table_cell

    return [panflute.TableRow(*map(to_table_cell, row)) for row in table_list]


def get_width_wrap(options, n_col, table_list):
    # parse width
    width = get_width(options, n_col)
    # auto-width when width is not specified
    if width is None:
        width = auto_width(get_table_width(options), n_col, table_list)
    return width


def get_caption(options):
    '''parsed as markdown into panflute AST if non-empty.'''
    return panflute.convert_text(str(options['caption']))[0].content if 'caption' in options else None


def csv_to_pipe_tables(table_list, caption, alignment):
    align_dict = {
        "AlignLeft": ':---',
        "AlignCenter": ':---:',
        "AlignRight": '---:',
        "AlignDefault": '---'
    }

    table_list.insert(1, [align_dict[key] for key in alignment])
    pipe_table_list = ['|\t{}\t|'.format('\t|\t'.join(map(str, row))) for row in table_list]
    if caption:
        pipe_table_list.append('')
        pipe_table_list.append(': {}'.format(caption))
    return '\n'.join(pipe_table_list)


def csv2pipe(options, data):
    """Construct pipe table directly.
    """
    # prepare table in list from data/include
    table_list = read_data(
        options.get('include', None),
        data
    )
    # delete element if table is empty (by returning [])
    # element unchanged if include is invalid (by returning None)
    if table_list is None:
        panflute.debug("pantable: include path not found. Codeblock shown as is.")
        # None means kept as is
        return
    elif table_list == []:
        panflute.debug("pantable: table is empty. Deleted.")
        # [] means delete the current element
        return []

    # regularize table: all rows should have same length
    n_col = regularize_table_list(table_list)

    # parse alignment
    alignment = parse_alignment(options.get('alignment', None), n_col)
    del n_col
    # get caption
    caption = options.get('caption', None)

    text = csv_to_pipe_tables(table_list, caption, alignment)

    raw_markdown = options.get('raw_markdown', False)
    if raw_markdown:
        # TODO: change this to 'markdown' once the PR accepted:
        # for now since pandoc treat all raw html as markdown it
        # will still works
        # https://github.com/sergiocorreia/panflute/pull/103
        return panflute.RawBlock(text, format='html')
    else:
        return panflute.convert_text(text)


def csv2table(options, data):
    """provided to panflute.yaml_filter to parse its content as pandoc table.
    """
    # prepare table in list from data/include
    table_list = read_data(
        options.get('include', None),
        data
    )
    # delete element if table is empty (by returning [])
    # element unchanged if include is invalid (by returning None)
    if table_list is None:
        panflute.debug("pantable: include path not found. Codeblock shown as is.")
        # None means kept as is
        return
    elif table_list == []:
        panflute.debug("pantable: table is empty. Deleted.")
        # [] means delete the current element
        return []

    # regularize table: all rows should have same length
    n_col = regularize_table_list(table_list)

    # Initialize the `options` output from `panflute.yaml_filter`
    width = get_width_wrap(options, n_col, table_list)
    # delete element if table is empty (by returning [])
    # width remains None only when table is empty
    if width is None:
        # debug info shown in auto_width
        return []

    # parse list to panflute table
    table_body = parse_table_list(
        options.get('markdown', False),
        table_list
    )
    del table_list
    # extract header row
    header_row = table_body.pop(0) if (
        len(table_body) > 1 and options.get('header', True)
    ) else None

    # parse alignment
    alignment = parse_alignment(options.get('alignment', None), n_col)
    del n_col
    # get caption
    caption = get_caption(options)

    return panflute.Table(
        *table_body,
        caption=caption,
        alignment=alignment,
        width=width,
        header=header_row
    )


def convert2table(options, data, **args):
    use_pipe_tables = options.get('pipe_tables', False)
    if use_pipe_tables:
        return csv2pipe(options, data)
    else:
        return csv2table(options, data)


def main(doc=None):
    """
    Fenced code block with class table will be parsed using
    panflute.yaml_filter with the fuction convert2table above.
    """
    return panflute.run_filter(
        panflute.yaml_filter,
        tag='table',
        function=convert2table,
        strict_yaml=True,
        doc=doc
    )


if __name__ == '__main__':
    main()
