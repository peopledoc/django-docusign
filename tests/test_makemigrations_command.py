from django.core.management import call_command

import pytest


@pytest.mark.parametrize("manage", [True, False, None])
def test_makemigrations(mocker, settings, manage):
    if manage is not None:
        settings.NORTH_MANAGE_DB = manage
    if manage is None and hasattr(settings, 'NORTH_MANAGE_DB'):
        del settings.NORTH_MANAGE_DB

    mock_handle = mocker.patch(
        'django.core.management.commands.makemigrations.Command.handle')

    call_command('makemigrations')

    assert mock_handle.called is False
