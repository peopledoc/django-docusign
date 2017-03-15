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

    NORTH_MANAGE_DB = True
    NORTH_MIGRATIONS_ROOT = '/path/to/sql/migrations/'
    NORTH_TARGET_VERSION = '1.42'

List of available settings:

* ``NORTH_MANAGE_DB``: if ``True``, the database will be managed by north.
  Default value ``False``
* ``NORTH_MIGRATIONS_ROOT``: a path to your migration repository. **required**
* ``NORTH_TARGET_VERSION``: the target SQL version
  (the version needed for your codebase). **required**
* ``NORTH_SCHEMA_TPL``: default value ``schema_{}.sql``
* ``NORTH_FIXTURES_TPL``: default value ``fixtures_{}.sql``
* ``NORTH_ADDITIONAL_SCHEMA_FILES``: list of sql files to load before the schema.
  For example: a file of DB roles, some extensions.
  Default value; ``[]``

In production environnements, ``NORTH_MANAGE_DB`` should be disabled, because
the database is managed directly by the DBA team (database as a service).

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

migrate
.......

.. code-block:: console

    $ ./tests_manage.py migrate

Create a DB from scratch and migrate it to the version defined in the
``NORTH_TARGET_VERSION`` setting, or update an existing DB to migrate it to
the correct version.

This command knows which migrations were already applied, which migrations
should be applied.

This command can only go forward: no possible revert like with south or django
migrations. But as the migrations written by the DBA team are blue/green, that
is not a problem !

This command has no effects if the ``NORTH_MANAGE_DB`` is disabled.

showmigrations
..............

.. code-block:: console

    $ ./tests_manage.py showmigrations

List available migrations, and indicate if they where applied or not.

This command has no effects if the ``NORTH_MANAGE_DB`` is disabled.

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
