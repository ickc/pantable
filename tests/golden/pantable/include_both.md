``` {.table include="include_rows.csv"}
---
# The attribute's file is appended first; then the include key reads the CSV
# from its own file, as it always has, and the rows in the block are not used.
include: csv_table_gbk.csv
include-encoding: gbk
---
```
