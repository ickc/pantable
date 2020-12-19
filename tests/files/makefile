SHELL = /usr/bin/env bash

PANTABLELOGLEVEL ?= DEBUG
pandoc ?= pandoc
_pandoc = PANTABLELOGLEVEL=$(PANTABLELOGLEVEL) $(pandoc)

MDFILES = $(wildcard md/*.md)
MDFILESOUTPUT = $(patsubst md/%.md,md_reference/%.md,$(MDFILES))
MDCODEBLOCKFILES = $(wildcard md_codeblock/*.md)
MDCODEBLOCKFILESOUTPUT = $(patsubst md_codeblock/%.md,md_codeblock_reference/%.md,$(MDCODEBLOCKFILES))
NATIVEFILES = $(wildcard native/*.native)
NATIVEFILESOUTPUT = $(patsubst native/%.native,native_reference/%.md,$(NATIVEFILES))

HTML = $(patsubst native/%.native,native/%.html,$(NATIVEFILES))

all: $(MDFILESOUTPUT) $(MDCODEBLOCKFILESOUTPUT) $(NATIVEFILESOUTPUT)

html: $(HTML)

md_reference/%.md: md/%.md
	cd ../..; $(_pandoc) -F pantable2csv -o tests/files/$@ tests/files/$<

md_codeblock_reference/%.md: md_codeblock/%.md
	cd ../..; $(_pandoc) -F pantable -o tests/files/$@ tests/files/$<

native_reference/%.md: native/%.native
	cd ../..; $(_pandoc) -F pantable2csvx -o tests/files/$@ tests/files/$<

native/%.html: native/%.native
	pandoc $< -s -o $@
