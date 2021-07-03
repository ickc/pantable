SHELL = /usr/bin/env bash

PANTABLELOGLEVEL ?= DEBUG
python ?= python
_python = PANTABLELOGLEVEL=$(PANTABLELOGLEVEL) $(python)
pandoc ?= pandoc
_pandoc = PANTABLELOGLEVEL=$(PANTABLELOGLEVEL) $(pandoc)
PYTESTPARALLEL ?= --workers auto
COVHTML ?= --cov-report html
# for bump2version, valid options are: major, minor, patch
PART ?= patch

pandocArgs = --toc -M date="`date "+%B %e, %Y"`" --filter=pantable --wrap=none

RSTs = CHANGELOG.rst README.rst

# Main Targets #################################################################

.PHONY: test docs-all docs html epub files dot clean Clean

all: dot files editable
	$(MAKE) test docs-all

test:
	$(_python) -m pytest -vv $(PYTESTPARALLEL) \
		--cov=src --cov-report term $(COVHTML) --no-cov-on-fail --cov-branch \
		tests

docs-all: docs html epub
docs: $(RSTs)
html: dist/docs/
epub: dist/epub/pantable.epub

files:
	cd tests/files; $(MAKE)
dot:
	cd docs/dot; $(MAKE)

clean:
	rm -f .coverage* docs/pantable*.rst docs/modules.rst docs/setup.rst
	rm -rf htmlcov pantable.egg-info .cache .idea dist docs/_build \
		docs/_static docs/_templates .ipynb_checkpoints .mypy_cache \
		.pytest_cache .tox
	find . -type f -name "*.py[co]" -delete \
		-or -type d -name "__pycache__" -delete
Clean: clean
	rm -f $(RSTs)

# maintenance ##################################################################

.PHONY: pypi pypiManual pep8 flake8 pylint
# Deploy to PyPI
## by CI, properly git tagged
pypi:
	git push origin v0.13.6
## Manually
pypiManual:
	rm -rf dist
	tox -e check
	poetry build
	twine upload dist/*

# check python styles
pep8:
	pycodestyle . --ignore=E501
flake8:
	flake8 . --ignore=E501
pylint:
	pylint pantable

print-%:
	$(info $* = $($*))

# docs #########################################################################

README.rst: docs/README.md docs/badges.csv
	printf \
		"%s\n\n" \
		".. This is auto-generated from \`$<\`. Do not edit this file directly." \
		> $@
	cd $(<D); \
	$(_pandoc) $(pandocArgs) $(<F) -V title='pantable Documentation' -s -t rst \
		>> ../$@

%.rst: %.md
	printf \
		"%s\n\n" \
		".. This is auto-generated from \`$<\`. Do not edit this file directly." \
		> $@
	$(_pandoc) $(pandocArgs) $< -s -t rst >> $@

dist/docs/:
	tox -e docs
# depends on docs as the api doc is built there
# didn't put this in tox as we should build this once every release
# TODO: consider put this in tox and automate it in GH Actions
dist/epub/pantable.epub: docs
	sphinx-build -E -b epub docs dist/epub
# the badges and dots has svg files that LaTeX complains about
# dist/pantable.pdf: docs
# 	sphinx-build -E -b latex docs dist/pdf
# 	cd dist/pdf; make
# 	mv dist/pdf/pantable.pdf dist

# poetry #######################################################################

# since poetry doesn't support editable, we can build and extract the setup.py,
# temporary remove pyproject.toml and ask pip to install from setup.py instead.
editable:
	poetry build
	cd dist; tar -xf pantable-0.13.6.tar.gz pantable-0.13.6/setup.py
	mv dist/pantable-0.13.6/setup.py .
	rm -rf dist/pantable-0.13.6
	mv pyproject.toml .pyproject.toml
	$(_python) -m pip install --no-dependencies -e .
	mv .pyproject.toml pyproject.toml
	rm -f setup.py

# releasing ####################################################################

bump:
	bump2version $(PART)
	git push --follow-tags
