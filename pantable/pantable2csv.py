#!/usr/bin/env python3

r"""
Panflute filter to convert any native pandoc tables into the CSV table format used by pantable:

- in code-block with class table
- metadata in YAML
- table in CSV

e.g.

~~~markdown
+--------+---------------------+--------------------------+
| First  | defaulted to be     | can be disabled          |
| row    | header row          |                          |
+========+=====================+==========================+
| 1      | cell can contain    | It can be aribrary block |
|        | **markdown**        | element:                 |
|        |                     |                          |
|        |                     | -   following standard   |
|        |                     |     markdown syntax      |
|        |                     | -   like this            |
+--------+---------------------+--------------------------+
| 2      | Any markdown        | $$E = mc^2$$             |
|        | syntax, e.g.        |                          |
+--------+---------------------+--------------------------+

: *Awesome* **Markdown** Table
~~~

becomes

~~~markdown
``` {.table}
---
alignment: DDD
caption: '*Awesome* **Markdown** Table'
header: true
markdown: true
table-width: 0.8055555555555556
width: [0.125, 0.3055555555555556, 0.375]
---
First row,defaulted to be header row,can be disabled
1,cell can contain **markdown**,"It can be aribrary block element:

-   following standard markdown syntax
-   like this
"
2,"Any markdown syntax, e.g.",$$E = mc^2$$
```
~~~
"""

import panflute
import io
import csv
import yaml


def ast2markdown(*ast):
    """
    convert a panflute ast into markdown
    """
    return panflute.convert_text(ast, input_format='panflute', output_format='markdown')


def get_table_options(elem):
    """
    parse the content of Table in ast and returns a dictionary of options
    """
    options = {}
    options['caption'] = elem.caption
    options['alignment'] = elem.alignment
    options['width'] = elem.width
    options['header'] = elem.header
    options['markdown'] = True
    return options


def parse_table_options(options):
    """
    parse the options
    """
    # caption: panflute ast to markdown
    if options['caption']:
        options['caption'] = ast2markdown(panflute.Para(*options['caption']))
    else:
        del options['caption']
    # parse alignment
    parsed_alignment = []
    for alignment in options['alignment']:
        if alignment == "AlignLeft":
            parsed_alignment.append("L")
        elif alignment == "AlignCenter":
            parsed_alignment.append("C")
        elif alignment == "AlignRight":
            parsed_alignment.append("R")
        elif alignment == "AlignDefault":
            parsed_alignment.append("D")
    options['alignment'] = "".join(parsed_alignment)
    # table-width from width
    options['table-width'] = sum(options['width'])
    # header: False if empty header row, else True
    options['header'] = bool(panflute.stringify(options['header']))
    return


def get_table_body(options, elem):
    """
    from elem, get full table body including header row if any
    """
    table_body = elem.content
    if options['header']:
        table_body.insert(0, elem.header)
    return table_body


def Table2list(Table):
    """
    convert a pandoc table into a 2D list
    """
    return [[ast2markdown(*cell.content) for cell in row.content] for row in Table]


def list2csv(table_list):
    with io.StringIO() as file:
        writer = csv.writer(file)
        writer.writerows(table_list)
        csv_table = file.getvalue()
    return csv_table


def options2yaml(options):
    return yaml.dump(options)


def table2csv(elem, doc):
    """
    find Table element and return a csv table in code-block with class "table"
    """
    if isinstance(elem, panflute.Table):
        # obtain options from Table
        options = get_table_options(elem)
        parse_table_options(options)
        # table in AST
        table_body = get_table_body(options, elem)
        # table in list
        table_list = Table2list(table_body)
        # table in CSV
        csv_table = list2csv(table_list)
        # option in YAML
        yaml_metadata = options2yaml(options)
        code_block = "---\n" + yaml_metadata + "---\n" + csv_table
        return panflute.CodeBlock(code_block, classes=["table"])
    return None


def main(_=None):
    """
    Any native pandoc tables will be converted into the CSV table format used by pantable:

    - in code-block with class table
    - metadata in YAML
    - table in CSV
    """
    panflute.run_filter(table2csv)

if __name__ == '__main__':
    main()
