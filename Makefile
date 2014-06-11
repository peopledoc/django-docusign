# Reference card for usual actions in development environment.
#
# For standard installation of django-docusign, see INSTALL.
# For details about django-docusign's development environment, see CONTRIBUTING.rst.
#
PIP = pip
TOX = tox
PROJECT = $(shell python -c "import setup; print setup.NAME")


.PHONY: help develop clean distclean maintainer-clean test documentation sphinx readme release


#: help - Display callable targets.
help:
	@echo "Reference card for usual actions in development environment."
	@echo "Here are available targets:"
	@egrep -o "^#: (.+)" [Mm]akefile  | sed 's/#: /* /'


#: develop - Install minimal development utilities.
develop:
	$(PIP) install tox
	$(PIP) install -e .


#: clean - Basic cleanup, mostly temporary files.
clean: clean-build clean-pyc
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete


#: distclean - Remove local builds, such as *.egg-info.
distclean: clean
	rm -rf *.egg
	rm -rf *.egg-info


#: maintainer-clean - Remove almost everything that can be re-generated.
maintainer-clean: distclean
	rm -rf build/
	rm -rf dist/
	rm -rf .tox/


#: test - Run test suites.
test:
	$(TOX)


#: documentation - Build documentation (Sphinx, README, ...)
documentation: sphinx readme


sphinx:
	$(TOX) -e sphinx


#: readme - Build standalone documentation files (README, CONTRIBUTING...).
readme:
	$(TOX) -e readme


#: release - Tag and push to PyPI.
release:
	$(TOX) -e release
