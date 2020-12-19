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
include: badges.csv
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

<https://ickc.github.io/pantable>

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
2,"Any markdown syntax, e.g.",E = mc^2^
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
2,"Any markdown syntax, e.g.",E = mc^2^
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

: the caption of the table. Can be block-like. If omitted, no caption will be inserted.
Interpreted as markdown only if `markdown: true` below.

    Default: disabled.

`short-caption`

: the short-caption of the table. Must be inline-like element.
Interpreted as markdown only if `markdown: true` below.

    Default: disabled.

`alignment`

: alignment for columns:
a string of characters among `L,R,C,D`, case-insensitive,
corresponds to Left-aligned, Right-aligned,
Center-aligned, Default-aligned respectively.
e.g. `LCRD` for a table with 4 columns.

    You can specify only the beginning that's non-default.
    e.g. `DLCR` for a table with 8 columns is equivalent to `DLCRDDDD`.

    Default: `DDD...`

`alignment-cells`

: alignment per cell. One row per line.
A string of characters among `L,R,C,D`, case-insensitive,
corresponds to Left-aligned, Right-aligned,
Center-aligned, Default-aligned respectively.
e.g.

        LCRD
        DRCL

    for a table with 4 columns, 2 rows.

    you can specify only the top left block that is not default, and the
    rest of the cells with be default to default automatically.
    e.g.

        DC
        LR

    for a table with 4 columns, 3 rows will be equivalent to

        DCDD
        LRDD
        DDDD

    Default: `DDD...\n...`

`width`

: a list of relative width corresponding to the width of each columns.
`D` means default width.
e.g.

    ```yaml
    - width
        - 0.1
        - 0.2
        - 0.3
        - 0.4
        - D
    ```

    Again, you can specify only the left ones that are non-default and it will be padded
    with defaults.

    Default: `[D, D, D, ...]`

`table-width`

: the relative width of the table (e.g. relative to `\linewidth`).
If specified as a number, and if any of the column width in `width` is default, then
auto-width will be performed such that the sum of `width` equals this number.

    Default: None

`header`

: If it has a header row or not.

    Default: True

`markdown`

: If CSV table cell contains markdown syntax or not.

     Default: False

`fancy_table`

: if true, then the first column of the table will be interpreted as a special fancy-table
    syntax s.t. it encodes which rows are

    - table-header,
    - table-foot,
    - multiple table-bodies and
    - "body-head" within table-bodies.

    see example below.

`include`
: the path to an CSV file, can be relative/absolute.
    If non-empty, override the CSV in the CodeBlock.

    Default: None

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

`format`

: The file format from the data in code-block or include if specified.

    Default: `csv` for data from code-block, and infer from extension in include.

    Currently only `csv` is supported.

`ms`

: (experimental, may drop in the future): a list of int that specifies the number of
    rows per row-block.
    e.g. `[2, 6, 3, 4, 5, 1]` means
    the table should have 21 rows,
    first 2 rows are table-head,
    last 1 row is table-foot,
    there are 2 table-bodies (indicated by `6, 3, 4, 5` in the middle)
    where the 1st body `6, 3` has 6 body-head and 3 "body-body",
    and the 2nd body `4, 5` has 4 body-head and 5 "body-body".

    If this is specified, `header` will be ignored.

    Default: None, which would be inferred from `header`.

`ns_head`

: (experimental, may drop in the future): a list of int that specifies the number of
    head columns per table-body.
    e.g. `[1, 2]` means
    the 1st table-body has 1 column of head,
    the 2nd table-body has 2 column of head

    Default: None

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

# Pantable as a library

![Overview](  docs/dot/pipeline-simple.svg)

![Detailed w/ methods](  docs/dot/pipeline.svg)

# Related Filters

The followings are pandoc filters written in Haskell that provide similar functionality. This filter is born after testing with theirs.

-   [baig/pandoc-csv2table: A Pandoc filter that renders CSV as Pandoc Markdown Tables.](https://github.com/baig/pandoc-csv2table)
-   [mb21/pandoc-placetable: Pandoc filter to include CSV data (from file or URL)](https://github.com/mb21/pandoc-placetable)
-   [sergiocorreia/panflute/csv-tables.py](https://github.com/sergiocorreia/panflute/blob/1ddcaba019b26f41f8c4f6f66a8c6540a9c5f31a/docs/source/csv-tables.py)

```table
---
Caption: Comparison
include: comparison.csv
...
```
