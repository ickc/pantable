#!/usr/bin/env python3

r"""
Panflute filter to parse table in fenced YAML code blocks.
Currently only CSV table is supported.

7 metadata keys are recognized:

-   caption: the caption of the table. If omitted, no caption will be inserted.
-   alignment: a string of characters among L,R,C,D, case-insensitive,
        corresponds to Left-aligned, Right-aligned,
        Center-aligned, Default-aligned respectively.
    e.g. LCRD for a table with 4 columns
    default: DDD...
-   width: a list of relative width corresponding to the width of each columns.
    default: auto calculate from the length of each line in table cells.
-   table-width: the relative width of the table (e.g. relative to \linewidth).
    default: 1.0
-   header: If it has a header row. default: true
-   markdown: If CSV table cell contains markdown syntax. default: False
-   include: the path to an CSV file.
    If non-empty, override the CSV in the CodeBlock.
    default: None

When the metadata keys is invalid, the default will be used instead.
Note that width and table-width accept fractions as well.

e.g.

```table
---
caption: '*Awesome* **Markdown** Table'
alignment: RC
table-width: 2/3
markdown: True
---
First row,defaulted to be header row,can be disabled
1,cell can contain **markdown**,"It can be aribrary block element:

- following standard markdown syntax
- like this"
2,"Any markdown syntax, e.g.",$$E = mc^2$$
```
"""

import csv
from fractions import Fraction
import io
import os
import panflute


# begin helper functions
def to_bool(to_be_bool, default=True):
    """
    Do nothing if to_be_bool is boolean,
    return `False` if it is "false" or "no" (case-insensitive),
    otherwise return default.
    """
    if not isinstance(to_be_bool, bool):
        str_bool = str(to_be_bool)
        if str_bool.lower() in ("false", "no"):
            to_be_bool = False
        elif str_bool.lower() in ("true", "yes"):
            to_be_bool = True
        else:
            to_be_bool = default
            panflute.debug("""pantable: invalid boolean. \
Should be true/false/yes/no, case-insensitive. Default is used.""")
    return to_be_bool


def get_width(options, number_of_columns):
    """
    get width: set to `None` when

    1. not given
    2. not a list
    3. length not equal to the number of columns
    4. negative entries
    """
    if 'width' not in options:
        width = None
    else:
        width = options['width']
        try:
            if len(width) != number_of_columns:
                raise ValueError
            width = [float(Fraction(x)) for x in options['width']]
            if not all(i >= 0 for i in width):
                raise ValueError
        except (ValueError, TypeError):
            width = None
            panflute.debug("pantable: invalid width")
    return width


def get_table_width(options):
    """
    `table-width` set to `1.0` if invalid
    """
    if 'table-width' not in options:
        table_width = 1.0
    else:
        try:
            table_width = float(Fraction(options.get('table-width')))
            if table_width <= 0:
                raise ValueError
        except (ValueError, TypeError):
            table_width = 1.0
            panflute.debug("pantable: invalid table-width")
    return table_width
# end helper functions


def get_include(options):
    """
    include set to None if invalid
    """
    if 'include' not in options:
        include = None
    else:
        include = str(options.get('include'))
        if not os.path.isfile(include):
            include = None
            panflute.debug("pantable: invalid path from 'include'")
    return include


def auto_width(table_width, number_of_columns, raw_table_list):
    """
    `width` is auto-calculated if not given in YAML
    It also returns isempty=True when table has 0 total width.
    """
    # calculate width
    width_abs = [max(
        [max(
            [len(line) for line in row[i].split("\n")]
        ) for row in raw_table_list]
    ) for i in range(number_of_columns)]
    try:
        if sum(width_abs) == 0:
            raise ValueError
        # match the way pandoc handle width, see jgm/pandoc commit 0dfceda
        width_abs = [each_width + 3 for each_width in width_abs]
        width_tot = sum(width_abs)
        width = [
            width_abs[i] / width_tot * table_width
            for i in range(number_of_columns)
        ]
    except ValueError:
        panflute.debug("pantable: table is empty")
        width = None
    return width


def parse_alignment(alignment_string, number_of_columns):
    """
    `alignment` string is parsed into pandoc format (AlignDefault, etc.)
    """
    # initialize
    alignment_string = str(alignment_string)
    number_of_alignments = len(alignment_string)
    # truncate and debug if too long
    if number_of_alignments > number_of_columns:
        alignment_string = alignment_string[:number_of_columns]
        panflute.debug("pantable: alignment string is too long")
    # parsing
    alignment = [("AlignLeft" if i.lower() == "l"
                  else "AlignCenter" if i.lower() == "c"
                  else "AlignRight" if i.lower() == "r"
                  else "AlignDefault" if i.lower() == "d"
                  else None) for i in alignment_string]
    # debug if invalid; set to default
    if None in alignment:
        alignment = [(i if i is not None else "AlignDefault")
                     for i in alignment]
        panflute.debug("pantable: alignment string is invalid")
    # fill up with default if too short
    if number_of_columns > number_of_alignments:
        alignment += ["AlignDefault" for __ in range(
            number_of_columns - len(alignment))]
    return alignment


def read_data(include, data):
    """
    read csv and return the table in list
    """
    if include is not None:
        with open(include) as file:
            raw_table_list = list(csv.reader(file))
    else:
        with io.StringIO(data) as file:
            raw_table_list = list(csv.reader(file))
    return raw_table_list


def regularize_table_list(raw_table_list):
    """
    When the length of rows are uneven, make it as long as the longest row.
    """
    max_number_of_columns = max(
        [len(row) for row in raw_table_list]
    )
    for row in raw_table_list:
        missing_number_of_columns = max_number_of_columns - len(row)
        if missing_number_of_columns > 0:
            row += ['' for __ in range(missing_number_of_columns)]
    return


def parse_table_list(markdown, raw_table_list):
    """
    read table in list and return panflute table format
    """
    table_body = []
    for row in raw_table_list:
        if markdown:
            cells = [
                panflute.TableCell(*panflute.convert_text(x))
                for x in row
            ]
        else:
            cells = [
                panflute.TableCell(panflute.Plain(panflute.Str(x)))
                for x in row
            ]
        table_body.append(panflute.TableRow(*cells))
    return table_body


def convert2table(options, data, **__):
    """
    provided to panflute.yaml_filter to parse its content as pandoc table.
    """
    # prepare table in list from data/include
    raw_table_list = read_data(get_include(options), data)
    # check empty table
    if not raw_table_list:
        panflute.debug("pantable: table is empty")
        return []
    # regularize table: all rows should have same length
    regularize_table_list(raw_table_list)
    # preparation: get no of columns of the table
    number_of_columns = len(raw_table_list[0])

    # Initialize the `options` output from `panflute.yaml_filter`
    # parse width
    width = get_width(options, number_of_columns)
    # auto-width when width is not specified
    if width is None:
        width = auto_width(get_table_width(
            options), number_of_columns, raw_table_list)
    # check empty table
    if width is None:
        panflute.debug("pantable: table is empty")
        return []
    # parse alignment
    alignment = parse_alignment(options.get(
        'alignment', None), number_of_columns)
    header = to_bool(options.get('header', True), True)
    markdown = to_bool(options.get('markdown', False), False)

    # get caption: parsed as markdown into panflute AST if non-empty.
    caption = panflute.convert_text(str(options['caption']))[
        0].content if 'caption' in options else None
    # parse list to panflute table
    table_body = parse_table_list(markdown, raw_table_list)
    # extract header row
    header_row = table_body.pop(0) if (
        len(table_body) > 1 and header
    ) else None
    return panflute.Table(
        *table_body,
        caption=caption,
        alignment=alignment,
        width=width,
        header=header_row
    )


def main(_=None):
    """
    Fenced code block with class table will be parsed using
    panflute.yaml_filter with the fuction convert2table above.
    """
    return panflute.run_filter(
        panflute.yaml_filter,
        tag='table',
        function=convert2table,
        strict_yaml=True
    )

if __name__ == '__main__':
    main()
