---
title: Examples
---

Each example is a short document on one topic, rendered with pantable.
Every page ends with its own Markdown source, the same with each table
as pandoc writes it, and the tables written back by `pantable2csvx`.
The test suite runs them too.

| Example                                  | Shows |
| ---------------------------------------- | ----- |
| [Basics](examples/basics.md)             | A CSV table in a code block, its caption, header and alignment |
| [Markdown cells](examples/markdown.md)   | `markdown: true`: Markdown in the cells and the caption |
| [Widths](examples/widths.md)             | `width` and `table-width` |
| [Including a CSV file](examples/include.md) | `include`, `include-encoding`, `csv-kwargs` |
| [Fancy tables](examples/fancy-table.md)  | Heads, feet, several bodies, spans and attributes, as `pantable2csvx` writes them |
| [Tables to CSV](examples/to-csv.md)      | `pantable2csv` and `pantable2csvx`, from pandoc's tables to code blocks |
