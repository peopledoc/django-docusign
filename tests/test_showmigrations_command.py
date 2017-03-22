from django.core.management import call_command
from django.utils.six import StringIO

import pytest


@pytest.mark.parametrize("manage", [True, False, None])
def test_migrate(mocker, settings, manage):
    if manage is not None:
        settings.NORTH_MANAGE_DB = manage
    if manage is None and hasattr(settings, 'NORTH_MANAGE_DB'):
        del settings.NORTH_MANAGE_DB

    mock_handle = mocker.patch(
        'django.core.management.commands.showmigrations.Command.handle')
    mock_plan = mocker.patch(
        'django_north.management.commands.showmigrations.Command.show_list')

    call_command('showmigrations')

    assert mock_handle.called is False
    assert mock_plan.called == bool(manage)


def test_showmigrations(mocker):
    mock_plan = mocker.patch(
        'django_north.management.migrations.build_migration_plan')

    # schema not inited
    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    mock_plan.return_value = None
    call_command('showmigrations')
    assert stdout.getvalue() == 'Schema not inited\n'

    # schema inited
    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    mock_plan.return_value = {
        'current_version': 'v2',
        'init_version': 'v1',
        'plans': [
            {
                'version': 'v3',
                'plan': [
                    ('a-ddl.sql', True, '/somewhere/a-ddl.sql'),
                    ('b-ddl.sql', False, '/somewhere/manual/b-ddl.sql'),
                ]
            },
            {
                'version': 'v4',
                'plan': [
                    ('a-ddl.sql', False, '/somewhere/a-ddl.sql'),
                ]
            }
        ],
    }
    call_command('showmigrations')
    assert stdout.getvalue() == (
        'Current version of the DB:\n'
        '  v2\n'
        'Schema used to init the DB:\n'
        '  v1\n'
        'Version:\n'
        '  v3\n'
        '  [X] a-ddl.sql\n'
        '  [ ] b-ddl.sql (manual)\n'
        'Version:\n'
        '  v4\n'
        '  [ ] a-ddl.sql\n'
    )
