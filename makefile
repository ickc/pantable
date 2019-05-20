SHELL = /usr/bin/env bash

# configure engine
python = python
pip = pip

pantable = 'pantable/pantable.py'
pantable2csv = 'pantable/pantable2csv.py'

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
	rm -f .coverage $(testAll)
	rm -rf htmlcov pantable.egg-info .cache .idea dist
	find . -type f -name "*.py[co]" -delete -or -type d -name "__pycache__" -delete

# Making dependancies #################################################################################################################################################################################

%.native: %.md
	pandoc -t native -F $(pantable) -o $@ $<

# maintenance #########################################################################################################################################################################################

# Deploy to PyPI
## by Travis, properly git tagged
pypi:
	git tag -a v$$($(python) setup.py --version) -m 'Deploy to PyPI' && git push origin v$$($(python) setup.py --version)
## Manually
pypiManual:
	$(python) setup.py sdist bdist_wheel && twine upload dist/*

pytest: $(testNative) tests/test_idempotent.native
	$(python) -m pytest -vv --cov=pantable tests
pytestLite:
	$(python) -m pytest -vv --cov=pantable tests
tests/reference_idempotent.native: tests/test_pantable.md
	pandoc -t native -F $(pantable) -F $(pantable2csv) -F $(pantable) -F $(pantable2csv) -o $@ $<
tests/test_idempotent.native: tests/reference_idempotent.native
	pandoc -f native -t native -F $(pantable) -F $(pantable2csv) -o $@ $<

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
