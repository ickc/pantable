SHELL = /usr/bin/env bash

pandocEngine ?= pdflatex
HTMLVersion ?= html5
PANTABLELOGLEVEL ?= DEBUG
python ?= python
_python = PANTABLELOGLEVEL=$(PANTABLELOGLEVEL) $(python)
pandoc ?= pandoc
_pandoc = PANTABLELOGLEVEL=$(PANTABLELOGLEVEL) $(pandoc)
PYTESTPARALLEL ?= --workers auto
EXTRAS ?=

# docs
CSSURL:=https://cdn.jsdelivr.net/gh/ickc/markdown-latex-css
pandocArgCommon = -f markdown+autolink_bare_uris-fancy_lists --toc -V linkcolorblue -V citecolor=blue -V urlcolor=blue -V toccolor=blue --pdf-engine=$(pandocEngine) -M date="`date "+%B %e, %Y"`"
## TeX/PDF
pandocArgFragment = $(pandocArgCommon) --filter=pantable
pandocArgStandalone = $(pandocArgFragment) --toc-depth=1 -s -N
## HTML/ePub
pandocArgHTML = $(pandocArgFragment) -t $(HTMLVersion) --toc-depth=2 -s -N -c $(CSSURL)/css/common.min.css -c $(CSSURL)/fonts/fonts.min.css
## GitHub README
pandocArgReadmeGitHub = $(pandocArgFragment) --toc-depth=2 -s -t markdown_github --reference-location=block
pandocArgReadmePypi = $(pandocArgFragment) -s -t rst --reference-location=block -f markdown+autolink_bare_uris-fancy_lists-implicit_header_references --wrap=none --columns=200

docsAll = CHANGELOG.rst README.rst

# Main Targets #################################################################

.PHONY: test testFull files clean

test:
	$(_python) -m pytest -vv $(PYTESTPARALLEL) --cov=src --cov-report term --no-cov-on-fail --cov-branch tests
pytest:
	$(_python) -m pytest -vv $(PYTESTPARALLEL) --cov=src --cov-report term --no-cov-on-fail --cov-branch tests --cov-report html
testFull: pytest pep8 pylint
files:
	cd tests/files; $(MAKE)
dot:
	cd dot; $(MAKE)

clean:
	cd docs && $(MAKE) clean
	rm -f .coverage $(docsAll) docs/pantable*.rst docs/modules.rst docs/setup.rst
	rm -rf htmlcov pantable.egg-info .cache .idea dist docs/_build docs/_static docs/_templates .ipynb_checkpoints .mypy_cache .pytest_cache README.html
	find . -type f \( -name "*.py[co]" -o -name ".coverage.*" \) -delete -or -type d -name "__pycache__" -delete
	[[ -d gh-pages ]] && find gh-pages -maxdepth 1 -mindepth 1 \! -name .git -exec rm -rf {} + || true

# maintenance ##################################################################

.PHONY: pypi pypiManual pep8 flake8 pylint autopep8 autopep8Aggressive
# Deploy to PyPI
## by CI, properly git tagged
pypi:
	git tag -a v$$($(_python) setup.py --version) -m 'Deploy to PyPI' && git push origin v$$($(_python) setup.py --version)
## Manually
pypiManual:
	$(_python) setup.py sdist bdist_wheel && twine upload dist/*

# check python styles
pep8:
	pycodestyle . --ignore=E501
flake8:
	flake8 . --ignore=E501
pylint:
	pylint pantable

# cleanup python
autopep8:
	autopep8 . --recursive --in-place --pep8-passes 2000 --verbose
autopep8Aggressive:
	autopep8 . --recursive --in-place --pep8-passes 2000 --verbose --aggressive --autopep8Aggressive

print-%:
	$(info $* = $($*))

# gh-pages #####################################################################

%.pdf: %.md
	$(_pandoc) $(pandocArgStandalone) -o $@ $<
%.html: %.md
	$(_pandoc) $(pandocArgHTML) $< -o $@

## PyPI README: not using this for now as rst2html emits errors
README.rst: docs/README.md docs/badges.csv
	printf "%s\n\n" ".. This is auto-generated from \`$<\`. Do not edit this file directly." > $@
	cd $(<D); $(_pandoc) $(pandocArgReadmePypi) $(<F) -V title='pantable Documentation' >> ../$@

%.rst: %.md
	printf "%s\n\n" ".. This is auto-generated from \`$<\`. Do not edit this file directly." > $@
	$(_pandoc) $< -s -t rst >> $@

# API docs #####################################################################

.PHONY: docs
docs: $(docsAll)
	sphinx-apidoc -d 10 -f -e -o $@ src
	cd $@ && $(MAKE) html

.PHONY: gh-pages
gh-pages:
	rsync -av --delete --stats --exclude='.git/' docs/_build/html/ gh-pages/
	cp -f docs/README.pdf gh-pages/

# poetry #####################################################################

# since poetry doesn't support editable, we can build and extract, copy the setup.py
# temporary remove pyproject.toml and ask pip to install from setup.py instead.
editable:
	poetry build
	cd dist; tar -xf pantable-0.13.0.tar.gz pantable-0.13.0/setup.py
	mv dist/pantable-0.13.0/setup.py .
	mv pyproject.toml .pyproject.toml
	$(_python) -m pip install -e .$(EXTRAS); mv .pyproject.toml pyproject.toml
