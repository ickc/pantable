---
title: Widths
---

`width` gives the relative width of each column, as a number or a
fraction; `D` leaves a column's width to the writer:

```table
---
width: [1/2, 1/4, D]
---
Description,Price,Stock
"A long description, which wraps in the space it has",1.34,12
Short,2.10,5
```

`table-width` is the width of the table, relative to the width of the
text. When some columns have no width, pantable gives them one, from
the length of their content, so that the widths add up to `table-width`:

```table
---
table-width: 2/3
---
Description,Price,Stock
"A long description, which wraps in the space it has",1.34,12
Short,2.10,5
```
