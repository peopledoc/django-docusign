============
Django North
============

.. image:: https://badge.fury.io/py/django-north.png
    :target: https://pypi.org/pypi/django-north

.. image:: https://travis-ci.org/novafloss/django-north.png?branch=master
    :target: https://travis-ci.org/novafloss/django-north

.. image:: https://img.shields.io/codecov/c/github/novafloss/django-north/master.svg
    :target: https://codecov.io/github/novafloss/django-north?branch=master

Yet another way to manage migrations: DBA as a service.

Let's your favorite DBAs define the database schema, and provide blue/green
migration files. Drop django native migrations, and use DBA's migrations
everywhere.

Requirements
------------

+ Django, obviously. v1.8 (for the moment)
+ Running under Python 2.7 (for the moment)

Documentation
-------------

The full documentation is at https://django-north.readthedocs.org.

Quickstart
----------

Install Django North::

    pip install django-north

In your ``settings.py`` :

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        "django_north",
    ]

    NORTH_ROOT = '/path/to/sql/migrations/')
    NORTH_TARGET_VERSION = '1.42'


Running Tests
--------------

You will need an usable a database in order to test the project. For example:

::

    source <YOURVIRTUALENV>/bin/activate
    export DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
    (myenv) $ pip install -r requirements_test.txt

Run tests for a specific version

::

    (myenv) $ ./runtest


Run tests for all versions (if tox is installed globally, you don't need a
virtual environment)

::

    $ tox

Using the project
-----------------

Many operations are documented in the Makefile. For more information, use:

::

    $ make help


Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
