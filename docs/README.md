---
fontsize:	11pt
documentclass:	memoir
classoption: article
geometry:	inner=1in, outer=1in, top=1in, bottom=1.25in
title:	Pantable—A Python library for writing pandoc filters for tables with batteries included.
...

``` {.table}
---
header: false
markdown: true
include: docs/badges.csv
...

The pantable package comes with 2 pandoc filters, `pantable` and `pantable2csv`. `pantable` is the main filter, introducing a syntax to include CSV table in markdown source. `pantable2csv` complements `pantable`, is the inverse of `pantable`, which convert native pandoc tables into the CSV table format defined by `pantable`.

Some example uses are:

1. You already have tables in CSV format.

2. You feel that directly editing markdown table is troublesome. You want a spreadsheet interface to edit, but want to convert it to native pandoc table for higher readability. And this process might go back and forth.

3. You want lower-level control on the table and column widths.

4. You want to use all table features supported by the pandoc's internal AST table format, which is not possible in markdown for pandoc \<= 1.18.^[In pandoc 1.19, grid-tables is improved to support all features available to the AST too.]

# Installation

    pip install pantable

You can also install the in-development version with:

    pip install https://github.com/ickc/pantable/archive/master.zip

# Documentation

<https://pantable.readthedocs.io/>

# Development

To run all the tests run:

    tox

Note, to combine the coverage data from all the tox environments run:

``` {.table}
---
width:
- 1/10
- 9/10
header: false
markdown: true
...
Windows,"    set PYTEST_ADDOPTS=--cov-append
    tox"
Other,    PYTEST_ADDOPTS=--cov-append tox
```

## Supported versions

pantable v0.12 drop Python 2 support. You need to install `pantable<0.12` if you need to run it on Python 2.

To enforce using Python 3, depending on your system, you may need to specify `python3` and `pip3` explicitly.

pandoc versioning semantics is [MAJOR.MAJOR.MINOR.PATCH](https://pvp.haskell.org) and pantable/panflute's is MAJOR.MINOR.PATCH. Below we shows matching versions of pandoc that pantable and panflute supports, in descending order. Only major version is shown as long as the minor versions doesn't matter.

| pantable | panflute version  | supported pandoc versions | supported pandoc API versions |
| --- | ---   | ---   |  ---  |
| TBA | 2.0 | 2.11.0.4—2.11.x  | 1.22    |
| - | not supported | 2.10  | 1.21  |
| 0.12 | 1.12 | 2.7-2.9 | 1.17.5–1.20  |

: Version Matching^[For pandoc API verion, check https://hackage.haskell.org/package/pandoc for pandoc-types, which is the same thing.]

Note: pandoc 2.10 is short lived and 2.11 has minor API changes comparing to that, mainly for fixing its shortcomings. Please avoid using pandoc 2.10.

To use pantable with pandoc < 2.10, install pantable 0.12 explicitly by `pip install pantable~=0.12.4`.

# `pantable`

This allows CSV tables, optionally containing markdown syntax (disabled by default), to be put in markdown as a fenced code blocks.

## Example

Also see the README in [GitHub Pages](https://ickc.github.io/pantable/). There's a [LaTeX output](https://ickc.github.io/pantable/README.pdf) too.

~~~
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
~~~

becomes

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

(The equation might not work if you view this on PyPI.)

## Usage

```bash
pandoc -F pantable -o README.html README.md
```

## Syntax

Fenced code blocks is used, with a class `table`. See [Example].

Optionally, YAML metadata block can be used within the fenced code block, following standard pandoc YAML metadata block syntax. 7 metadata keys are recognized:

`caption`

: the caption of the table. If omitted, no caption will be inserted.
    Default: disabled.

`alignment`

: a string of characters among `L,R,C,D`, case-insensitive,
        corresponds to Left-aligned, Right-aligned,
        Center-aligned, Default-aligned respectively.
    e.g. `LCRD` for a table with 4 columns.
    Default: `DDD...`

`width`

: a list of relative width corresponding to the width of each columns.
    e.g.

    ```yaml
    - width
        - 0.1
        - 0.2
        - 0.3
        - 0.4
    ```

    Default: auto calculated from the length of each line in table cells.

`table-width`

: the relative width of the table (e.g. relative to `\linewidth`).
    default: 1.0

`header`
: If it has a header row or not.
    True/False/yes/NO are accepted, case-insensitive.
    default: True

`markdown`
: If CSV table cell contains markdown syntax or not.
     Same as above.
     Default: False

`include`
: the path to an CSV file, can be relative/absolute.
    If non-empty, override the CSV in the CodeBlock.
    default: None

`include-encoding`
: if specified, the file from `include` will be decoded according to this encoding, else assumed to be UTF-8. Hint: if you save the CSV file via Microsoft Excel, you may need to set this to `utf-8-sig`.

`csv-kwargs`
: If specified, should be a dictionary passed to `csv.reader` as options. e.g.
    ```yaml
    ---
    csv-kwargs:
      dialect: unix
      key: value...
    ...
    ```

`pipe_tables`

: If True, a pipe table will be constructed directly in markdown syntax instead of via AST. `markdown` is implied to be True. `header` will be overridden as true because `pipe_tables` must has header in pandoc.

    This trades correctness for speed. It won't be correct if any of the cell is multiline for example, resulting in an invalid pipe table. However, it is much faster comparing to previous `markdown: True` case because previously per cell a subprocess to execute pandoc the parse the markdown to AST is needed.

`grid_tables`

: If True, a grid table will be constructed directly in markdown syntax instead of via AST. `markdown` is implied to be True. `header` can be used together with this.

    This trades correctness for speed. This should be more robust than `pipe_tables` since the `grid_tables` syntax supports everything the pandoc AST supports. This however depends on an external dependency. Install it by either `pip install terminaltables` or `conda install terminaltables`.

`raw_markdown`

: If True, force output the table as a pipe table (which is tab-delimited.) This is sometimes useful if pandoc is very stubborn to not emit a pipe table even if `markdown-grid_tables...` is used. Note that this should only be used if the output format is markdown.

When the metadata keys is invalid, the default will be used instead.
Note that width and table-width accept fractions as well.

# `pantable2csv`

This one is the inverse of `pantable`, a panflute filter to convert any native pandoc tables into the CSV table format used by pantable.

Effectively, `pantable` forms a "CSV Reader", and `pantable2csv` forms a "CSV Writer". It allows you to convert back and forth between these 2 formats.

For example, in the markdown source:

~~~
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

running `pandoc -F pantable2csv -o output.md input.md`{.bash}, it becomes

~~~
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

# Related Filters

The followings are pandoc filters written in Haskell that provide similar functionality. This filter is born after testing with theirs.

-   [baig/pandoc-csv2table: A Pandoc filter that renders CSV as Pandoc Markdown Tables.](https://github.com/baig/pandoc-csv2table)
-   [mb21/pandoc-placetable: Pandoc filter to include CSV data (from file or URL)](https://github.com/mb21/pandoc-placetable)
-   [sergiocorreia/panflute/csv-tables.py](https://github.com/sergiocorreia/panflute/blob/1ddcaba019b26f41f8c4f6f66a8c6540a9c5f31a/docs/source/csv-tables.py)

```table
---
Caption: Comparison
include: docs/comparison.csv
...
```
