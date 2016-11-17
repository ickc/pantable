SHELL := /usr/bin/env bash

# command line arguments
pandocArgCommon := -f markdown+autolink_bare_uris-fancy_lists --toc --normalize -S -V linkcolorblue -V citecolor=blue -V urlcolor=blue -V toccolor=blue --latex-engine=$(pandocEngine) -M date="`date "+%B %e, %Y"`"
# Workbooks
## MD
pandocArgMD := -f markdown+abbreviations+autolink_bare_uris+markdown_attribute+mmd_header_identifiers+mmd_link_attributes+mmd_title_block+tex_math_double_backslash-latex_macros-auto_identifiers -t markdown+raw_tex-native_spans-simple_tables-multiline_tables-grid_tables-latex_macros --normalize -s --wrap=none --column=999 --atx-headers --reference-location=block --file-scope
## TeX/PDF
### LaTeX workflow
latexmkArg := -$(latexmkEngine)
pandocArgFragment := $(pandocArgCommon) --top-level-division=part --filter=$(filterPath)/pandoc-amsthm.py
### pandoc workflow
pandocArgStandalone := $(pandocArgFragment) --toc-depth=1 -s -N -H workbook-template.tex -H workbook.sty
## HTML/ePub
pandocArgHTML := $(pandocArgFragment) -t $(HTMLVersion) --toc-depth=2 -s -N -H workbook-template.html -H $(mathjaxPath)/setup-mathjax-cdn.html --mathjax -c $(CSSURL)/css/common.css -c $(CSSURL)/fonts/fonts.css
pandocArgePub := $(pandocArgHTML) -t $(ePubVersion) -H $(mathjaxPath)/load-mathjax-cdn.html --epub-chapter-level=2
# GitHub README
pandocArgReadmeGitHub := $(pandocArgCommon) --toc-depth=2 -s -t markdown_github --reference-location=block

# Main Targets ########################################################################################################################################################################################

# autopep8
pep8:
	find . -maxdepth 2 -iname "*.py" | xargs -i -n1 -P8 autopep8 --in-place --aggressive --aggressive {}

# update submodule
update:
	git submodule update --recursive --remote

# Automation on */*.md, in the order from draft to finish #############################################################################################################################################

# cleanup source code
cleanup: style normalize
## Normalize white spaces:
### 1. Add 2 trailing newlines
### 2. transform non-breaking space into (explicit) space
### 3. temporarily transform markdown non-breaking space `\ ` into unicode
### 4. delete all CONSECUTIVE blank lines from file except the first; deletes all blank lines from top and end of file; allows 0 blanks at top, 0,1,2 at EOF
### 5. delete trailing whitespace (spaces, tabs) from end of each line
### 6. revert (3)
normalize:
	find . -maxdepth 2 -mindepth 2 -iname "*.md" | xargs -i -n1 -P8 bash -c 'printf "\n\n" >> "$$0" && sed -i -e "s/ / /g" -e '"'"'s/\\ / /g'"'"' -e '"'"'/./,/^$$/!d'"'"' -e '"'"'s/[ \t]*$$//'"'"' -e '"'"'s/ /\\ /g'"'"' $$0' {}
## pandoc cleanup:
### 1. pandoc from markdown to markdown
### 2. transform unicode non-breaking space back to `\ `
style:
	find . -maxdepth 2 -mindepth 2 -iname "*.md" | xargs -i -n1 -P8 bash -c 'pandoc $(pandocArgMD) -o $$0 $$0 && sed -i -e '"'"'s/ /\\ /g'"'"' $$0' {}
