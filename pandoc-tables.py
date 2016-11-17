#!/usr/bin/env python3

"""
Panflute filter to parse table in fenced YAML code blocks.
Currently only CSV table is supported.

7 metadata keys are recognized:

-   caption: the caption of the table. If omitted, no caption will be inserted.
-   alignment: a string of characters among L,R,C,D, case-insensitive,
    corresponds to Left-aligned, Right-aligned, Center-aligned, Default-aligned respectively.
    e.g. LCRD for a table with 4 columns
    default: DDD...
-   width: a list of relative width corresponding to the width of each columns.
    default: auto calculate from the length of line in a (potentially multiline) cell.
-   table-width: the relative width of the table (comparing to, say, \linewidth).
    default: 1.0
-   header: If it has a header row. default: true
-   markdown: If CSV table cell contains markdown syntax. default: True
-   include: the path to an CSV file. If non-empty, override the CSV in the CodeBlock.
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

def get_table_options(options):
    """
    It parses the options output from `panflute.yaml_filter` and
    return it as variables `(caption, alignment, width, table_width, header, markdown)`.
    """
    caption = options.get('caption')
    alignment = options.get('alignment')
    width = options.get('width')
    table_width = options.get('table-width',1.0)
    header = options.get('header',True)
    markdown = options.get('markdown',True)
    include = options.get('include',None)
    return (caption, alignment, width, table_width, header, markdown, include)

def check_table_options(width, table_width, header, markdown, include):
    """
    It sets the varaibles to default if they are invalid:
    
    - `width` set to `None` when invalid, each element in `width` set to `0` when negative
    - `table_width`: set to `1.0` if invalid or not positive
    - set `header` to `True` if invalid
    - set `markdown` to `True` if invalid
    """
    try:
        width = [(float(x) if float(x) >= 0 else 0) for x in width]
    except (TypeError, ValueError):
        width = None
    try:
        table_width = float(table_width) if float(table_width) > 0 else 1.0
    except (TypeError, ValueError):
        table_width = 1.0
    header = to_bool(header)
    markdown = to_bool(markdown)
    if include != None:
        if not os.path.isfile(include):
            include = None
    return (width, table_width, header, markdown, include)

def parse_table_options(caption, alignment, width, table_width, raw_table_list):
    """
    `caption` is assumed to contain markdown, as in standard pandoc YAML metadata
    `alignment` string is parsed into pandoc format (AlignDefault, etc.)
    `width` is auto-calculated if not given in YAML
    """
    # parse caption
    if caption != None:
        caption = panflute.convert_text(str(caption))[0].content
    # preparation: get no of columns of the table
    number_of_columns = len(raw_table_list[0])
    ## parse alignment
    if alignment != None:
        alignment = str(alignment)
        parsed_alignment = []
        for i in range(number_of_columns):
            try:
                if alignment[i].lower() == "l":
                    parsed_alignment.append("AlignLeft")
                elif alignment[i].lower() == "c":
                    parsed_alignment.append("AlignCenter")
                elif alignment[i].lower() == "r":
                    parsed_alignment.append("AlignRight")
                else:
                    parsed_alignment.append("AlignDefault")
            except IndexError:
                for i in range(number_of_columns-len(parsed_alignment)):
                    parsed_alignment.append("AlignDefault")
        alignment = parsed_alignment
    # calculate width
    if width == None:
        width_abs = [max([max([len(line) for line in row[i].split("\n")]) for row in raw_table_list]) for i in range(number_of_columns)]
        width_tot = sum(width_abs)
        try:
            width = [width_abs[i]/width_tot*table_width for i in range(number_of_columns)]
        except ZeroDivisionError:
            width = None
    return (caption, alignment, width)

def read_csv(data, include):
    """
    read csv and return the table in list
    """
    if include != None:
        with open(include) as f:
            raw_table_list = list(csv.reader(f))
    else:
        with io.StringIO(data) as f:
            raw_table_list = list(csv.reader(f))
    return raw_table_list

def parse_table_list(raw_table_list, markdown):
    """
    read table in list and return panflute table format
    """
    body = []
    for row in raw_table_list:
        if markdown:
            cells = [panflute.TableCell(*panflute.convert_text(x)) for x in row]
        else:
            cells = [panflute.TableCell(panflute.Plain(panflute.Str(x))) for x in row]
        body.append(panflute.TableRow(*cells))
    return body

def convert2table(options, data, element, doc):
    # get table options from YAML metadata
    caption, alignment, width, table_width, header, markdown, include = get_table_options(options)
    # check table options
    width, table_width, header, markdown, include = check_table_options(width, table_width, header, markdown, include)
    # parse csv to list
    raw_table_list = read_csv(data, include)
    # parse list to panflute table
    body = parse_table_list(raw_table_list, markdown)
    # parse table options
    caption, alignment, width = parse_table_options(caption, alignment, width, table_width, raw_table_list)
    # finalize table according to metadata
    header_row = body.pop(0) if header else None
    table = panflute.Table(*body, caption=caption, alignment=alignment, width=width, header=header_row)
    return table

# We'll only run this for CodeBlock elements of class 'table'
def main(doc=None):
     return panflute.run_filter(panflute.yaml_filter, tag='table', function=convert2table, strict_yaml=True)

if __name__ == '__main__':
    main()