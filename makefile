SHELL := /usr/bin/env bash

test := $(wildcard tests/*.md)
native := $(patsubst %.md,%.native,$(test))
pdf := $(patsubst %.md,%.pdf,$(test))

filter := pandoc_tables/pandoc_tables.py

# Main Targets ########################################################################################################################################################################################

all: $(native) $(pdf)
travis: $(native)

tests/%.native: tests/%.md $(filter)
	pandoc -t native -F $(filter) -o $@ $<

tests/%.pdf: tests/%.md $(filter)
	pandoc -F $(filter) -o $@ $<

clean:
	rm -f $(native) $(pdf)

# maintenance #########################################################################################################################################################################################

init:
	pip install -r requirements.txt

test: $(native)
	py.test tests

# check python
check:
	pep8 .

# cleanup python
pep8:
	# find . -maxdepth 2 -mindepth 2 -iname "*.py" | xargs -i -n1 -P8 autopep8 {} --in-place
	autopep8 . --recursive --in-place --pep8-passes 2000 --verbose

# cleanup markdown
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
	find . -maxdepth 2 -mindepth 2 -iname "*.md" | xargs -i -n1 -P8 bash -c 'pandoc -o $$0 $$0 && sed -i -e '"'"'s/ /\\ /g'"'"' $$0' {}
