# Comparison

``` {.table}
---
table-width: 1.3
---
,pandoc-csv2table,pandoc-placetable,panflute example,my proposal
type,type=simple|multiline|grid|pipe,,,
header,header=yes|no,header=yes|no,header: True|False,header: True|False
caption,caption,caption,title,caption
source,source,file,source,include
aligns,aligns=LRCD,aligns=LRCD,,alignment: LRCD
width,,"widths=""0.5 0.2 0.3""",,"column-width: [0.5, 0.2, 0.3]"
,,inlinemarkdown,,markdown: True|False
,,delimiter,,
,,quotechar,,
,,id (wrapped by div),,
```

# Simple Test

``` {.table}
**_Fruit_**,~~Price~~,_Number_,`Advantages`
*Bananas~1~*,$1.34,12~units~,"Benefits of eating bananas
(**Note the appropriately
rendered block markdown**):

- _built-in wrapper_
- ~~**bright color**~~

"
*Oranges~2~*,$2.10,5^10^~units~,"Benefits of eating oranges:

- **cures** scurvy
- `tasty`"
```

# Full Test

``` {.table}
---
caption: "*Great* Title"
alignment: LRC
width:
  - 0.1
  - 0.2
  - 0.3
  - 0.4
header: False
markdown: True
...
**_Fruit_**,~~Price~~,_Number_,`Advantages`
*Bananas~1~*,$1.34,12~units~,"Benefits of eating bananas
(**Note the appropriately
rendered block markdown**):

- _built-in wrapper_
- ~~**bright color**~~

"
*Oranges~2~*,$2.10,5^10^~units~,"Benefits of eating oranges:

- **cures** scurvy
- `tasty`"
```

# Testing Wrong Type

``` {.table}
**_Fruit_**,~~Price~~,_Number_,`Advantages`
*Bananas~1~*,$1.34,12~units~,"Benefits of eating bananas
(**Note the appropriately
rendered block markdown**):

- _built-in wrapper_
- ~~**bright color**~~

---
caption: 0.1
header: IDK
markdown: true
...

"
*Oranges~2~*,$2.10,5^10^~units~,"Benefits of eating oranges:

- **cures** scurvy
- `tasty`"

---
width:
- -0.1
- -0.2
- -0.3
- -0.4
alignment: 0.1
---
```



# Include External CSV

``` {.table}
---
caption: "*Great* Title"
header: True
markdown: True
alignment: AlignLeft, AlignRight, AlignCenter, AlignDefault
include: tests/csv_tables.csv
...
```

# Empty CSV

``` {.table}
---
...
```

# Testing 0 Table Width

``` {.table}
,
,
```

# Irregular CSV

``` {.table}
---
markdown: False
...
2,3,4,5,6,7
1
```

# Invalid YAML
``` {.table}
---
caption: *unquoted*
...
1,2
3,4
```

# One Row Table

``` {.table}
1,2
```
