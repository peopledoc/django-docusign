=====
Usage
=====

Configuration
-------------

In your ``settings.py`` :

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        "django_north",
    ]

    NORTH_MIGRATIONS_ROOT = '/path/to/sql/migrations/')
    NORTH_TARGET_VERSION = '1.42'

List of available settings:

* ``NORTH_MIGRATIONS_ROOT``: a path to your migration repository. **required**
* ``NORTH_TARGET_VERSION``: the target SQL version. **required**
  (the version needed for your codebase)
* ``NORTH_SCHEMA_TPL``: default value ``schema_{}.sql``


Migration repository tree example:

.. code-block:: console

    1.0/
        manual/
            1.0-feature_a-020-dml.sql
        1.0-0-version-dml.sql
        1.0-feature_a-010-ddl.sql
    1.1/
        1.1-0-version-dml.sql
    2.0/
        2.0-0-version-dml.sql
    2.1/
        2.1-0-version-dml.sql
    fixtures/
        fixtures_1.0.sql
        fixtures_1.1.sql
        fixtures_2.0.sql
    schemas/
        schema_1.0.sql
        schema_1.1.sql
        schema_2.0.sql

See also some examples in ``tests/data`` folder.

Available Commands
------------------

showfixtures
............

.. code-block:: console

    $ ./tests_manage.py showfixtures

List missing fixtures, and print SQL instructions to create them
(ask your DBA team to add a dml migration for that).

"Fixtures" designates here datas which are automatically created by django
on ``post_migrate`` signal, and required for the project.


Basically:

* content types (``django.contrib.contenttypes``)
* permissions (``django.contrib.auth``)

The site id 1 (``SITE_ID`` setting) is not checked by this command.
