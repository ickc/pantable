SHELL = /usr/bin/env bash

# configure engine
python = python
pip = pip

test = $(wildcard tests/*.md)
testNative = $(patsubst %.md,%.native,$(test))
testAll = $(testNative)

# Main Targets ########################################################################################################################################################################################

.PHONY: all docs test testFull clean

all: $(testAll)

docs:
	cd docs && make -j

test: pytest
	coverage html
testFull: pytest pep8 pylint
	coverage html

clean:
	rm -f .coverage $(testAll) tests/reference_idempotent.native
	rm -rf htmlcov pantable.egg-info .cache .idea dist
	find . -type f \( -name "*.py[co]" -o -name ".coverage.*" \) -delete -or -type d -name "__pycache__" -delete
	find tests -name '*.pdf' -delete

# Making dependancies #################################################################################################################################################################################

%.native: %.md
	pandoc -t json $< | coverage run --append --branch -m pantable.cli.pantable | pandoc -f json -t native -o $@

# maintenance #########################################################################################################################################################################################

# Deploy to PyPI
## by CI, properly git tagged
pypi:
	git tag -a v$$($(python) setup.py --version) -m 'Deploy to PyPI' && git push origin v$$($(python) setup.py --version)
## Manually
pypiManual:
	$(python) setup.py sdist bdist_wheel && twine upload dist/*

pytest: $(testNative) tests/test_idempotent.native
	$(python) -m pytest -vv --cov=pantable --cov-branch tests
pytestLite:
	$(python) -m pytest -vv --cov=pantable --cov-branch --cov-append tests
tests/reference_idempotent.native: tests/test_pantable.md
	pandoc -t json $< |\
		coverage run --append --branch -m pantable.cli.pantable | coverage run --append --branch -m pantable.cli.pantable2csv |\
		coverage run --append --branch -m pantable.cli.pantable | coverage run --append --branch -m pantable.cli.pantable2csv |\
		pandoc -f json -t native > $@
tests/test_idempotent.native: tests/reference_idempotent.native
	pandoc -f native -t json $< |\
		coverage run --append --branch -m pantable.cli.pantable | coverage run --append --branch -m pantable.cli.pantable2csv |\
		pandoc -f json -t native > $@

# check python styles
pep8:
	pycodestyle . --ignore=E402,E501,E731
pylint:
	pylint pantable

# cleanup python
autopep8:
	autopep8 . --recursive --in-place --pep8-passes 2000 --verbose
autopep8Aggressive:
	autopep8 . --recursive --in-place --pep8-passes 2000 --verbose --aggressive --autopep8Aggressive

print-%:
	$(info $* = $($*))
