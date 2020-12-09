SHELL = /usr/bin/env bash

PANTABLELOGLEVEL ?= DEBUG
pandoc ?= PANTABLELOGLEVEL=$(PANTABLELOGLEVEL) pandoc

MDFILES = $(wildcard md/*.md)
MDFILESOUTPUT = $(patsubst md/%.md,md_reference/%.md,$(MDFILES))
MDCODEBLOCKFILES = $(wildcard md_codeblock/*.md)
MDCODEBLOCKFILESOUTPUT = $(patsubst md_codeblock/%.md,md_codeblock_reference/%.md,$(MDCODEBLOCKFILES))
NATIVEFILES = $(wildcard native/*.native)
NATIVEFILESOUTPUT = $(patsubst native/%.native,native_reference/%.md,$(NATIVEFILES))

all: $(MDFILESOUTPUT) $(MDCODEBLOCKFILESOUTPUT) $(NATIVEFILESOUTPUT)

md_reference/%.md: md/%.md
	cd ../..; $(pandoc) -F pantable2csv -o tests/files/$@ tests/files/$<

md_codeblock_reference/%.md: md_codeblock/%.md
	cd ../..; $(pandoc) -F pantable -o tests/files/$@ tests/files/$<

native_reference/%.md: native/%.native
	cd ../..; $(pandoc) -F pantable2csvx -o tests/files/$@ tests/files/$<
