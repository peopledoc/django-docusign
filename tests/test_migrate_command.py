import os.path

from django.core.management import call_command
from django.utils.six import StringIO

import pytest

from django_north.management.commands import migrate


@pytest.mark.parametrize("manage", [True, False, None])
def test_migrate(mocker, settings, manage):
    if manage is not None:
        settings.NORTH_MANAGE_DB = manage
    if manage is None and hasattr(settings, 'NORTH_MANAGE_DB'):
        del settings.NORTH_MANAGE_DB

    mock_handle = mocker.patch(
        'django.core.management.commands.migrate.Command.handle')
    mock_migrate = mocker.patch(
        'django_north.management.commands.migrate.Command.migrate')

    call_command('migrate')

    assert mock_handle.called is False
    assert mock_migrate.called == bool(manage)


def test_migrate_run_script(settings, mocker):
    root = os.path.dirname(__file__)
    settings.NORTH_MIGRATIONS_ROOT = os.path.join(root, 'test_data/sql')

    mock_run = mocker.patch('django_north.management.runner.Script.run')

    command = migrate.Command()

    path = os.path.join(settings.NORTH_MIGRATIONS_ROOT,
                        '16.12/16.12-0-version-dml.sql')
    command.run_script(path)
    assert len(mock_run.call_args_list) == 1


def test_migrate_init_schema(settings, mocker):
    root = os.path.dirname(__file__)
    settings.NORTH_MIGRATIONS_ROOT = os.path.join(root, 'test_data/sql')

    mocker.patch(
        'django_north.management.migrations.get_version_for_init',
        return_value='16.12')
    mock_run_script = mocker.patch(
        'django_north.management.commands.migrate.Command.run_script')

    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    command = migrate.Command()
    command.verbosity = 2

    # no additional files
    if hasattr(settings, 'NORTH_ADDITIONAL_SCHEMA_FILES'):
        del settings.NORTH_ADDITIONAL_SCHEMA_FILES
    command.init_schema()
    assert len(mock_run_script.call_args_list) == 2
    assert mock_run_script.call_args_list[0] == mocker.call(
        os.path.join(settings.NORTH_MIGRATIONS_ROOT, 'schemas',
                     'schema_16.12.sql'))
    assert mock_run_script.call_args_list[1] == mocker.call(
        os.path.join(settings.NORTH_MIGRATIONS_ROOT, 'fixtures',
                     'fixtures_16.12.sql'))
    assert stdout.getvalue() == (
        'Load schema\n'
        '  Applying 16.12...\n'
        'Load fixtures\n'
        '  Applying 16.12...\n'
    )

    mock_run_script.reset_mock()
    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    command = migrate.Command()
    command.verbosity = 2

    # extensions & fixtures
    settings.NORTH_ADDITIONAL_SCHEMA_FILES = ['extension.sql']
    command.init_schema()
    assert len(mock_run_script.call_args_list) == 3
    assert mock_run_script.call_args_list[0] == mocker.call(
        os.path.join(settings.NORTH_MIGRATIONS_ROOT, 'schemas',
                     'extension.sql'))
    assert mock_run_script.call_args_list[1] == mocker.call(
        os.path.join(settings.NORTH_MIGRATIONS_ROOT, 'schemas',
                     'schema_16.12.sql'))
    assert mock_run_script.call_args_list[2] == mocker.call(
        os.path.join(settings.NORTH_MIGRATIONS_ROOT, 'fixtures',
                     'fixtures_16.12.sql'))
    assert stdout.getvalue() == (
        'Load extension.sql\n'
        'Load schema\n'
        '  Applying 16.12...\n'
        'Load fixtures\n'
        '  Applying 16.12...\n'
    )

    mock_run_script.reset_mock()
    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    command = migrate.Command()
    command.verbosity = 2

    # extensions, roles & fixtures
    settings.NORTH_ADDITIONAL_SCHEMA_FILES = ['extension.sql', 'roles.sql']
    command.init_schema()
    assert len(mock_run_script.call_args_list) == 4
    assert mock_run_script.call_args_list[0] == mocker.call(
        os.path.join(settings.NORTH_MIGRATIONS_ROOT, 'schemas',
                     'extension.sql'))
    assert mock_run_script.call_args_list[1] == mocker.call(
        os.path.join(settings.NORTH_MIGRATIONS_ROOT, 'schemas',
                     'roles.sql'))
    assert mock_run_script.call_args_list[2] == mocker.call(
        os.path.join(settings.NORTH_MIGRATIONS_ROOT, 'schemas',
                     'schema_16.12.sql'))
    assert mock_run_script.call_args_list[3] == mocker.call(
        os.path.join(settings.NORTH_MIGRATIONS_ROOT, 'fixtures',
                     'fixtures_16.12.sql'))
    assert stdout.getvalue() == (
        'Load extension.sql\n'
        'Load roles.sql\n'
        'Load schema\n'
        '  Applying 16.12...\n'
        'Load fixtures\n'
        '  Applying 16.12...\n'
    )

    mock_run_script.reset_mock()
    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    command = migrate.Command()
    command.verbosity = 2

    # no fixtures
    mocker.patch(
        'django_north.management.migrations.get_version_for_init',
        return_value='17.3')
    del settings.NORTH_ADDITIONAL_SCHEMA_FILES
    command.init_schema()
    assert len(mock_run_script.call_args_list) == 1
    assert mock_run_script.call_args_list[0] == mocker.call(
        os.path.join(settings.NORTH_MIGRATIONS_ROOT, 'schemas',
                     'schema_17.3.sql'))
    assert stdout.getvalue() == (
        'Load schema\n'
        '  Applying 17.3...\n'
    )


def test_migrate_nomigration_plan(mocker):
    mock_run_script = mocker.patch(
        'django_north.management.commands.migrate.Command.run_script')
    mock_init_schema = mocker.patch(
        'django_north.management.commands.migrate.Command.init_schema')
    mock_record = mocker.patch(
        'django_north.management.migrations.MigrationRecorder'
        '.record_applied'
    )

    mocker.patch(
        'django_north.management.migrations.build_migration_plan',
        side_effect=[
            None,
            {
                'current_version': 'v2',
                'init_version': 'v1',
                'plans': [
                    {
                        'version': 'v3',
                        'plan': [
                            ('v3-a-ddl.sql', True, '/somewhere/v3-a-ddl.sql'),
                            ('v3-b-ddl.sql', False,
                             '/somewhere/manual/v3-b-ddl.sql'),
                        ]
                    },
                    {
                        'version': 'v4',
                        'plan': [
                            ('v4-a-ddl.sql', False, '/somewhere/v4-a-ddl.sql'),
                        ]
                    }
                ],
            }
        ])

    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    call_command('migrate')
    assert len(mock_init_schema.call_args_list) == 1
    assert mock_run_script.call_args_list == [
        mocker.call('/somewhere/manual/v3-b-ddl.sql'),
        mocker.call('/somewhere/v4-a-ddl.sql'),
    ]
    assert mock_record.call_args_list == [
        mocker.call('v3', 'v3-b-ddl.sql'),
        mocker.call('v4', 'v4-a-ddl.sql'),
    ]
    assert stdout.getvalue() == (
        'v3\n'
        '  v3-a-ddl.sql already applied\n'
        '  Applying v3-b-ddl.sql (manual)...\n'
        'v4\n'
        '  Applying v4-a-ddl.sql...\n'
    )


def test_migrate_with_migration_plan(mocker):
    mock_run_script = mocker.patch(
        'django_north.management.commands.migrate.Command.run_script')
    mock_init_schema = mocker.patch(
        'django_north.management.commands.migrate.Command.init_schema')
    mock_record = mocker.patch(
        'django_north.management.migrations.MigrationRecorder'
        '.record_applied')

    mocker.patch(
        'django_north.management.migrations.build_migration_plan',
        return_value={
            'current_version': 'v2',
            'init_version': 'v1',
            'plans': [
                {
                    'version': 'v3',
                    'plan': [
                        ('v3-a-ddl.sql', True, '/somewhere/v3-a-ddl.sql'),
                        ('v3-b-ddl.sql', False,
                         '/somewhere/manual/v3-b-ddl.sql'),
                    ]
                },
                {
                    'version': 'v4',
                    'plan': [
                        ('v4-a-ddl.sql', False, '/somewhere/v4-a-ddl.sql'),
                    ]
                }
            ],
        })

    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    call_command('migrate')
    assert mock_init_schema.called is False
    assert mock_run_script.call_args_list == [
        mocker.call('/somewhere/manual/v3-b-ddl.sql'),
        mocker.call('/somewhere/v4-a-ddl.sql'),
    ]
    assert mock_record.call_args_list == [
        mocker.call('v3', 'v3-b-ddl.sql'),
        mocker.call('v4', 'v4-a-ddl.sql'),
    ]
    assert stdout.getvalue() == (
        'v3\n'
        '  v3-a-ddl.sql already applied\n'
        '  Applying v3-b-ddl.sql (manual)...\n'
        'v4\n'
        '  Applying v4-a-ddl.sql...\n'
    )
