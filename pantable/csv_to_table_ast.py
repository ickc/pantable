#!/usr/bin/env python

r"""Panflute filter to parse CSV table in fenced YAML code blocks."""

import fractions

import panflute

from .read_csv import parse_alignment, read_csv, regularize_table_list
from .util import EmptyTableError


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
        raise EmptyTableError

    # The +3 match the way pandoc handle width, see jgm/pandoc commit 0dfceda
    scale = table_width / (width_tot + 3 * n_col)
    return [(width + 3) * scale for width in max_col_width]


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


def csv_to_table_ast(options, data):
    """provided to panflute.yaml_filter to parse its content as pandoc table.
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

    # Initialize the `options` output from `panflute.yaml_filter`
    width = get_width_wrap(options, n_col, table_list)

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
