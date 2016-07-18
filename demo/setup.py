# -*- coding: utf-8 -*-
"""Python packaging."""
import os

from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.dirname(here)


NAME = 'django-docusign-demo'
DESCRIPTION = ''
README = open(os.path.join(here, 'README.rst')).read()
VERSION = open(os.path.join(project_root, 'VERSION')).read().strip()
AUTHOR = u'Benoît Bryon'
EMAIL = u'novafloss@people-doc.com'
URL = ''
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2.7',
    'Framework :: Django']
KEYWORDS = []
PACKAGES = ['django_docusign_demo']
REQUIREMENTS = [
    'django-docusign',
    'django-formsetfield',
    'django-nose',
    'setuptools',
]
ENTRY_POINTS = {
    'console_scripts': [
        'django-docusign-demo = django_docusign_demo.manage:main',
    ]
}


if __name__ == '__main__':  # Don't run setup() when we import this module.
    setup(name=NAME,
          version=VERSION,
          description=DESCRIPTION,
          long_description=README,
          classifiers=CLASSIFIERS,
          keywords=' '.join(KEYWORDS),
          author=AUTHOR,
          author_email=EMAIL,
          url=URL,
          license='BSD',
          packages=PACKAGES,
          include_package_data=True,
          zip_safe=False,
          install_requires=REQUIREMENTS,
          entry_points=ENTRY_POINTS)
