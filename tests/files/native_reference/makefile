SHELL = /usr/bin/env bash

MDs = $(wildcard *.md)
HTMLs = $(patsubst %.md,%.html,$(MDs))
PDFs = $(patsubst %.md,%.pdf,$(MDs))

all: $(HTMLs) $(PDFs)

%.html: %.md
	pandoc -s -o $@ $< -F pantable

%.pdf: %.md
	pandoc -s -o $@ $< -F pantable
