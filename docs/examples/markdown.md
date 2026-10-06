---
title: Markdown cells
---

By default, a cell is plain text. With `markdown: true`, the cells and
the caption are Markdown, and a cell may hold any block, such as a list.
A cell that spans lines is quoted, as in any CSV:

```table
---
caption: '*Awesome* **Markdown** Table'
short-caption: Markdown Table
markdown: true
---
First row,defaulted to be header row,can be disabled
1,cell can contain **markdown**,"It can be an arbitrary block element:

- following standard markdown syntax
- like this"
2,"Any markdown syntax, e.g.",E = mc^2^
```

`short-caption` is the caption for a list of tables, such as LaTeX's
`\listoftables`.

Without `markdown: true`, the same characters are text:

```table
Syntax,Shown as
**bold**,**bold**
`code`,`code`
```
