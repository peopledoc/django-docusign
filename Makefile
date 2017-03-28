.PHONY: clean-pyc clean-build docs help
.DEFAULT_GOAL := help

TOX = tox

help:
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

clean: clean-build clean-pyc

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint: ## check style with flake8
	flake8 --exclude="migrations,.tox,docs,build" .

test: ## run tests quickly with the default Python
	./runtests

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	COVERAGE=1 ./runtests

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/django-north.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ django_north
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

release: clean  ## release - Tag and push to PyPI
	$(TOX) -e release
