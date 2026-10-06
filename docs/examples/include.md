---
title: Including a CSV file
---

`include` reads the table from a file, relative to the directory pandoc
runs in, instead of the code block, which can be empty:

```table
---
caption: Fruits, from fruits.csv
include: fruits.csv
---
```

`include-encoding` sets the file's encoding when it is not UTF-8. A CSV
file saved by Microsoft Excel may need `utf-8-sig`.

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
