SHELL := /usr/bin/env bash

# dot, neato, twopi, circo, fdp, sfdp, patchwork, osage
DOT ?= dot

FONT ?= "Latin Modern Roman"

DOTs = $(wildcard *.dot) pipeline-simple.dot
SVGs = $(patsubst %.dot,%.svg,$(DOTs))

svg: $(SVGs)

# remove edge label
pipeline-simple.dot: pipeline.dot
	sed -E -e 's/->(.*)label="[^"]+",? ?/->\1/' -e 's/ \[\]//' $< > $@

pipeline-simple.svg: DOT=sfdp

%.svg: %.dot
	$(DOT) -T svg $< -o $*.svg -Nfontname=$(FONT) -Efontname=$(FONT) -Gfontname=$(FONT)
	svgcleaner --multipass $*.svg $*.svg

clean:
	rm -f $(SVGs)

print-%:
	$(info $* = $($*))
