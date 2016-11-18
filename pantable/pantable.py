#!/usr/bin/env python3

"""
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
-   markdown: If CSV table cell contains markdown syntax. default: True
-   include: the path to an CSV file.
    If non-empty, override the CSV in the CodeBlock.
    default: None

When the metadata keys is invalid, the default will be used instead.

e.g.

```markdown
~~~table
---
caption: "*Great* Title"
alignment: LRC
width:
  - 0.1
  - 0.2
  - 0.3
  - 0.4
header: False
markdown: True
...
**_Fruit_**,~~Price~~,_Number_,`Advantages`
*Bananas~1~*,$1.34,12~units~,"Benefits of eating bananas
(**Note the appropriately
rendered block markdown**):

- _built-in wrapper_
- ~~**bright color**~~

"
*Oranges~2~*,$2.10,5^10^~units~,"Benefits of eating oranges:

- **cures** scurvy
- `tasty`"
~~~
```
"""

import io
import os
import csv
import panflute


def to_bool(x):
    """
    Do nothing if x is boolean,
    return `False` if it is "false" or "no" (case-insensitive),
    otherwise return `True`.
    """
    if not isinstance(x, bool):
        if str(x).lower() in ("false", "no"):
            x = False
        else:
            x = True
    return x


def init_table_options(options):
    """
    Initialize the `options` output from `panflute.yaml_filter`.
    """
    options['caption'] = options.get('caption', None)
    options['alignment'] = options.get('alignment', None)
    options['width'] = options.get('width', None)
    options['table-width'] = options.get('table-width', 1.0)
    options['header'] = options.get('header', True)
    options['markdown'] = options.get('markdown', True)
    options['include'] = options.get('include', None)
    return options


def check_table_options(options):
    """
    Set the values in options to default if they are invalid:

    -   `width` set to `None` when invalid,
        each element in `width` set to `0` when negative
    -   `table-width` set to `1.0` if invalid or not positive
    -   `header` set to `True` if invalid
    -   `markdown` set to `True` if invalid
    """
    try:
        options['width'] = [
            (float(x) if float(x) >= 0 else 0)
            for x in options['width']
        ]
    except (ValueError, TypeError):
        options['width'] = None
    try:
        options['table-width'] = (
            float(options['table-width'])
            if float(options['table-width']) > 0
            else 1.0
        )
    except ValueError:
        options['table-width'] = 1.0
    options['header'] = to_bool(options['header'])
    options['markdown'] = to_bool(options['markdown'])
    if options['include'] is not None:
        if not os.path.isfile(options['include']):
            options['include'] = None
    return options


def parse_table_options(options, raw_table_list):
    """
    `caption` is assumed to contain markdown,
        as in standard pandoc YAML metadata.
    `alignment` string is parsed into pandoc format (AlignDefault, etc.)
    `width` is auto-calculated if not given in YAML
    """
    # parse caption
    if options['caption'] is not None:
        options['caption'] = panflute.convert_text(
            str(options['caption'])
        )[0].content
    # preparation: get no of columns of the table
    number_of_columns = len(raw_table_list[0])
    # parse alignment
    if options['alignment'] is not None:
        options['alignment'] = str(options['alignment'])
        parsed_alignment = []
        for i in range(number_of_columns):
            try:
                if options['alignment'][i].lower() == "l":
                    parsed_alignment.append("AlignLeft")
                elif options['alignment'][i].lower() == "c":
                    parsed_alignment.append("AlignCenter")
                elif options['alignment'][i].lower() == "r":
                    parsed_alignment.append("AlignRight")
                else:
                    parsed_alignment.append("AlignDefault")
            except IndexError:
                for i in range(number_of_columns - len(parsed_alignment)):
                    parsed_alignment.append("AlignDefault")
        options['alignment'] = parsed_alignment
    # calculate width
    if options['width'] is None:
        width_abs = [max(
            [max(
                [len(line) for line in row[i].split("\n")]
            ) for row in raw_table_list]
        ) for i in range(number_of_columns)]
        width_tot = sum(width_abs)
        try:
            options['width'] = [
                width_abs[i] / width_tot * options['table-width']
                for i in range(number_of_columns)
            ]
        except ZeroDivisionError:
            options['width'] = None
    return options


def read_csv(include, data):
    """
    read csv and return the table in list
    """
    if include is not None:
        with open(include) as f:
            raw_table_list = list(csv.reader(f))
    else:
        with io.StringIO(data) as f:
            raw_table_list = list(csv.reader(f))
    return raw_table_list


def regularize_table_list(raw_table_list):
    max_number_of_columns = max(
        [len(row) for row in raw_table_list]
    )
    for row in raw_table_list:
        if len(row) < max_number_of_columns:
            for i in range(max_number_of_columns - len(row)):
                row.append('')
    return raw_table_list


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


def convert2table(options, data, element, doc):
    # initialize table options from YAML metadata
    options = init_table_options(options)
    # check table options
    options = check_table_options(options)
    # parse csv to list
    raw_table_list = read_csv(options['include'], data)
    # check empty table
    if raw_table_list == []:
        return []
    # regularize table: all rows should have same length
    raw_table_list = regularize_table_list(raw_table_list)
    # parse list to panflute table
    table_body = parse_table_list(options['markdown'], raw_table_list)
    # parse table options
    options = parse_table_options(options, raw_table_list)
    # finalize table according to metadata
    header_row = table_body.pop(0) if options['header'] else None
    table = panflute.Table(
        *table_body,
        caption=options['caption'],
        alignment=options['alignment'],
        width=options['width'],
        header=header_row
    )
    return table


def main(doc=None):
    # We'll only run this for CodeBlock elements of class 'table'
    return panflute.run_filter(
        panflute.yaml_filter,
        tag='table',
        function=convert2table,
        strict_yaml=True
    )

if __name__ == '__main__':
    main()
