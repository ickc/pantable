---
title: Including a CSV file
---

The code block's `include` attribute reads the table from a file. The
block holds the options, or nothing:

```{.table include="fruits.csv"}
---
caption: Fruits, from fruits.csv
---
```

The file's text is appended to the block's: an empty block's text
becomes the file's, and a block with text of its own keeps it, the
file's text on the next line. So rows in the block come before the
file's, and when the block has no YAML block and the file begins with
one, it sets the options, as it would if written in the block. The file
is read as UTF-8, its line endings as `\n`, without a byte order mark or
its final newline; an empty file adds nothing.

This is what [panclude](https://github.com/ickc/panclude) does to a code
block with an `include` attribute, so
`pandoc -L panclude.lua -F pantable` makes the same table: either may do
the including, and after panclude pantable sees an ordinary code block.
When pantable does it:

- a relative path starts at the directory pandoc runs in, where panclude
  starts at the document's: the two agree when pandoc runs from the
  document's directory;
- panclude's other attributes, `startLine`, `endLine`, `dedent` and
  `raw`, are not read: the whole file is included, with a warning;
- a file that cannot be read (missing, a directory, not UTF-8) leaves the
  code block as it is, with an error naming the path, as panclude leaves
  it.

The `include` key in the YAML block is still supported. It reads the CSV
from its file instead of the block's rows, relative to the directory
pandoc runs in, and `include-encoding` sets that file's encoding when it
is not UTF-8 (a CSV file saved by Microsoft Excel may need `utf-8-sig`):

```table
---
caption: Fruits, from fruits.csv
include: fruits.csv
---
```

Given both, the attribute's file is appended first, then the key reads
the CSV from its own file, as it always has.

Apart from `include`, the options are read from the YAML block only, as
with any other table, and not from attributes on the code block such as
`{.table caption="..."}`.

`csv-kwargs` is passed to Python's
[`csv.reader`](https://docs.python.org/3/library/csv.html#csv.reader),
here to read semicolon-separated values:

```table
---
csv-kwargs:
  delimiter: ;
---
Fruit;Price
Bananas;1,34
Oranges;2,10
```

Here, for values in single quotes, after a comma and a space:

```table
---
csv-kwargs:
  quotechar: "'"
  skipinitialspace: true
---
Prefix, City, Comment
'030', 'Berlin', 'My comment'
'069', 'Frankfurt', 'Main, not Oder'
```
