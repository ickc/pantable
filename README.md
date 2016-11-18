-   [CSV Tables in Markdown: Pandoc Filter for CSV Tables](#csv-tables-in-markdown-pandoc-filter-for-csv-tables)
-   [Example](#example)
-   [Install and Use](#install-and-use)
-   [Syntax](#syntax)
-   [Related Filters](#related-filters)

CSV Tables in Markdown: Pandoc Filter for CSV Tables
====================================================

This allows CSV tables, optionally containing markdown syntax (enabled by default), to be put in markdown as a fenced code blocks.

Example
=======

This won’t work on GitHub’s markdown rendering. See the README in [GitHub-pages](https://ickc.github.io/pantable).

    ```table
    ---
    caption: '*Awesome* **Markdown** Table'
    alignment: RC
    table-width: 0.7
    ---
    First row,defaulted to be header row,can be disabled
    1,cell can contain **markdown**,"It can be aribrary block element:

    - following standard markdown syntax
    - like this"
    2,"Any markdown syntax, e.g.",$$E = mc^2$$
    ```

becomes

``` table
---
caption: '*Awesome* **Markdown** Table'
alignment: RC
table-width: 0.7
---
First row,defaulted to be header row,can be disabled
1,cell can contain **markdown**,"It can be aribrary block element:

- following standard markdown syntax
- like this"
2,"Any markdown syntax, e.g.",$$E = mc^2$$
```

Install and Use
===============

Install:

``` bash
pip install -U pantable
```

Use:

``` bash
pandoc -F pantable -o README.html README.md
```

Syntax
======

Fenced code blocks is used, with a class `table`. See [Example](#example).

Optionally, YAML metadata block can be used within the fenced code block, following standard pandoc YAML metadata block syntax. 7 metadata keys are recognized:

-   `caption`: the caption of the table. If omitted, no caption will be inserted. Default: disabled.

-   `alignment`: a string of characters among `L,R,C,D`, case-insensitive, corresponds to Left-aligned, Right-aligned, Center-aligned, Default-aligned respectively. e.g. `LCRD` for a table with 4 columns. Default: `DDD...`

-   `width`: a list of relative width corresponding to the width of each columns. e.g.

    ``` yaml
    - width
        - 0.1
        - 0.2
        - 0.3
        - 0.4
    ```

    Default: auto calculated from the length of each line in table cells.

-   `table-width`: the relative width of the table (e.g. relative to `\linewidth`). default: 1.0

-   `header`: If it has a header row or not. True/False/yes/NO are accepted, case-insensitive. default: True

-   `markdown`: If CSV table cell contains markdown syntax or not. Same as above. Default: True

-   `include`: the path to an CSV file, can be relative/absolute. If non-empty, override the CSV in the CodeBlock. default: None

When the metadata keys is invalid, the default will be used instead.

Related Filters
===============

The followings are pandoc filters written in Haskell that provide similar functionality. This filter is born after testing with theirs.

-   [baig/pandoc-csv2table: A Pandoc filter that renders CSV as Pandoc Markdown Tables.](https://github.com/baig/pandoc-csv2table)
-   [mb21/pandoc-placetable: Pandoc filter to include CSV data (from file or URL)](https://github.com/mb21/pandoc-placetable)
-   [panflute/csv-tables.py at 1ddcaba019b26f41f8c4f6f66a8c6540a9c5f31a · sergiocorreia/panflute](https://github.com/sergiocorreia/panflute/blob/1ddcaba019b26f41f8c4f6f66a8c6540a9c5f31a/docs/source/csv-tables.py)

``` table
---
Caption: Comparison
include: docs/comparison.csv
...
```
