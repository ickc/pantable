---
title: Fancy tables
---

pandoc's tables have more than a header and rows: a table head and
foot, several bodies, each with rows of its own head, and columns of
row heads, cells that span rows and columns, and attributes on all of
these. With `fancy-table: true`, the first column of the CSV holds what
CSV cannot:

- A marker ends a block of rows: `===` the table head when it is first,
  and the table foot when it is last; `---` the head rows of a body;
  `___` a body's other rows.
- `{#id .class key=value}` before a marker gives the block attributes,
  and after it, the row.
- A cell whose first line is `(rows, columns)` spans that many, and
  `{...}` on that line gives the cell attributes.
- `ns-head` is the number of columns of row heads in each body.

This is how `pantable2csvx` writes any pandoc table, losslessly. The
table of planets from pandoc's test suite:

``` table
---
alignment: CCDRRRRRRRR
caption: Data about the planets of our solar system.
fancy-table: true
markdown: true
ns-head:
- 3
...
===,"(1, 2)
",,Name,Mass (10\^24kg),Diameter (km),Density (kg/m\^3),Gravity (m/s\^2),Length of day (hours),Distance from Sun (10\^6km),Mean temperature (C),Number of moons,Notes
,"(4, 2)
Terrestrial planets",,Mercury,0.330,"4,879",5427,3.7,4222.6,57.9,167,0,Closest to the Sun
,,,Venus,4.87,"12,104",5243,8.9,2802.0,108.2,464,0,
,,,Earth,5.97,"12,756",5514,9.8,24.0,149.6,15,1,Our world
,,,Mars,0.642,"6,792",3933,3.7,24.7,227.9,-65,2,The red planet
,"(4, 1)
Jovian planets","(2, 1)
Gas giants",Jupiter,1898,"142,984",1326,23.1,9.9,778.6,-110,67,The largest planet
,,,Saturn,568,"120,536",687,9.0,10.7,1433.5,-140,62,
,,"(2, 1)
Ice giants",Uranus,86.8,"51,118",1271,8.7,17.2,2872.5,-195,27,
,,,Neptune,102,"49,528",1638,11.0,16.1,4495.1,-200,14,
___,"(1, 2)
Dwarf planets",,Pluto,0.0146,"2,370",2095,0.7,153.3,5906.4,-225,5,Declassified as a planet in 2006.
```

Nordic countries, with attributes on the table, its blocks, rows and
cells:

``` {#nordics .table source="wikipedia"}
---
alignment: CLLL
alignment-cells: CCCC
caption: States belonging to the *Nordics.*
fancy-table: true
markdown: true
ms:
- 1
- 0
- 5
- 1
ns-head:
- 1
short-caption: Nordic countries
width:
- 3/10
- 3/10
- 1/5
- 1/5
...
{.simple-head} ===,Name,Capital,"Population\
(in 2018)","Area\
(in km^2^)"
{.country},Denmark,Copenhagen,"5,809,502","43,094"
{.country},Finland,Helsinki,"5,537,364","338,145"
{.country},Iceland,Reykjavik,"343,518","103,000"
{.country},Norway,Oslo,"5,372,191","323,802"
{.souvereign-states} ___ {.country},Sweden,Stockholm,"10,313,447","450,295"
=== {#summary},Total,,"{#total-population}
27,376,022","{#total-area}
1,258,336"
```
