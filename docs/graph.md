---
title: "Graph"
description: "Every page, and the links between them."
format: html
comments: false
exclude-in-listing: true
page-layout: full
toc: false
title-block-banner: false
---

<!-- SHARED FILE from https://github.com/ickc/quarto-template (the post graph,
opt-in): do not edit it in a site. graph.json, paragraphic.js and
paragraphic.css are written into the site root after the render, by
paragraphic's post-render step. -->

Every page on this site, and the links between them. A dot's size is how many pages it links to or is linked from,
and its colour is the part of the site it is in. Hover over a dot to see what it is connected to, click it to open
the page, or type in the box to find one by its title.

```{=html}
<link rel="stylesheet" href="paragraphic.css">
<div class="paragraphic" data-src="graph.json"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script src="paragraphic.js"></script>
```
