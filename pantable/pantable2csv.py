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


def table2csv(elem, doc):
    """
    find Table element and return a csv table in code-block with class "table"
    """
    if isinstance(elem, panflute.Table):
        # get options as a dictionary
        options = {}
        # options: caption: panflute ast to markdown
        if elem.caption:
            options['caption'] = panflute.convert_text(
                panflute.Para(*elem.caption),
                input_format='panflute',
                output_format='markdown'
            )
        # options: alignment
        parsed_alignment = [("L" if i == "AlignLeft"
                             else "C" if i == "AlignCenter"
                             else "R" if i == "AlignRight"
                             else "D") for i in elem.alignment]
        options['alignment'] = "".join(parsed_alignment)
        # options: width
        options['width'] = elem.width
        # options: table-width from width
        options['table-width'] = sum(options['width'])
        # options: header: False if empty header row, else True
        options['header'] = bool(panflute.stringify(elem.header))
        # options: markdown
        options['markdown'] = True

        # option in YAML
        yaml_metadata = yaml.dump(options)

        # table in panflute AST
        table_body = elem.content
        if options['header']:
            table_body.insert(0, elem.header)
        # table in list
        table_list = [
            [panflute.convert_text(
                cell.content,
                input_format='panflute',
                output_format='markdown'
            ) for cell in row.content]
            for row in table_body]
        # table in CSV
        with io.StringIO() as file:
            writer = csv.writer(file)
            writer.writerows(table_list)
            csv_table = file.getvalue()
        return panflute.CodeBlock("---\n" + yaml_metadata + "---\n" + csv_table, classes=["table"])
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
