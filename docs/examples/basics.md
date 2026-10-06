---
title: Basics
---

A fenced code block with the class `table` holds a table as CSV. The
first row is the header:

```table
Planet,Moons,Rings
Earth,1,No
Jupiter,95,Yes
Saturn,146,Yes
```

A YAML block at the top of the code block sets the options. Here,
`caption` and `alignment`: one letter per column among `L`, `R`, `C`
and `D` (left, right, centre, default), and the columns left out are
default:

```table
---
caption: The outer planets
alignment: LRC
---
Planet,Moons,Rings
Jupiter,95,Yes
Saturn,146,Yes
Uranus,28,Yes
Neptune,16,Yes
```

With `header: false`, every row is in the body:

```table
---
header: false
---
Mercury,0
Venus,0
```

`alignment-cells` aligns cells one by one, a line per row, and again
what is left out is default:

```table
---
alignment-cells: |
  CC
  LR
---
Planet,Moons
Mars,2
Earth,1
```
