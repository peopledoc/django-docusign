#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python packaging."""
import os
import sys

from setuptools import setup


#: Absolute path to directory containing setup.py file.
here = os.path.abspath(os.path.dirname(__file__))
#: Boolean, ``True`` if environment is running Python version 2.
IS_PYTHON2 = sys.version_info[0] == 2


NAME = 'django-docusign'
DESCRIPTION = 'Django application for DocuSign signature SAAS platform.'
README = open(os.path.join(here, 'README.rst')).read()
VERSION = open(os.path.join(here, 'VERSION')).read().strip()
AUTHOR = u'Benoît Bryon'
EMAIL = u'novafloss@people-doc.com'
LICENSE = 'BSD'
URL = 'https://{name}.readthedocs.io/'.format(name=NAME)
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2.7',
    'Framework :: Django',
]
KEYWORDS = [
    'docusign',
    'signature',
    'backend',
    'pydocusign',
    'django-anysign',
]
PACKAGES = [NAME.replace('-', '_')]
REQUIREMENTS = [
    'Django<1.8',
    'django-anysign>=0.3',
    'pydocusign>=0.13.1',
    'setuptools',
]
if IS_PYTHON2:
    REQUIREMENTS.append('mock')
ENTRY_POINTS = {}
TEST_REQUIREMENTS = []
CMDCLASS = {}
SETUP_REQUIREMENTS = [
    'setuptools'
]


# Tox integration.
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    """Test command that runs tox."""
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox  # import here, cause outside the eggs aren't loaded.
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


TEST_REQUIREMENTS.append('tox')
CMDCLASS['test'] = Tox


if __name__ == '__main__':  # Do not run setup() when we import this module.
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=README,
        classifiers=CLASSIFIERS,
        keywords=' '.join(KEYWORDS),
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        license=LICENSE,
        packages=PACKAGES,
        include_package_data=True,
        zip_safe=False,
        install_requires=REQUIREMENTS,
        entry_points=ENTRY_POINTS,
        tests_require=TEST_REQUIREMENTS,
        cmdclass=CMDCLASS,
        setup_requires=SETUP_REQUIREMENTS,
    )
