---
title: Tables to CSV
---

`pantable2csv` is the other way round: it writes each pandoc table as
pantable's code block, so that a table can go back and forth between a
spreadsheet and Markdown:

```sh
pandoc -F pantable2csv -t markdown -o output.md input.md
```

`pantable2csvx` writes [fancy tables](fancy-table.md), which hold all of
a pandoc table. `pantable2csv` writes plain CSV, and leaves out what it
cannot hold, such as several bodies or cells spanning rows.

The tabs at the end of this page show what `pantable2csvx` writes for
the tables here, such as this grid table:

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

and this pipe table:

| Right | Left | Default | Center |
|------:|:-----|---------|:------:|
|   12  |  12  |    12   |    12  |
|  123  |  123 |   123   |   123  |
|    1  |    1 |     1   |     1  |

: A pipe table
