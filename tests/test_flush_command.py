from django.core.management import call_command

import pytest


@pytest.mark.parametrize("manage", [True, False, None])
def test_flush(mocker, settings, manage):
    if manage is not None:
        settings.NORTH_MANAGE_DB = manage
    if manage is None and hasattr(settings, 'NORTH_MANAGE_DB'):
        del settings.NORTH_MANAGE_DB

    mock_handle = mocker.patch(
        'django.core.management.commands.flush.Command.handle')
    mock_flush = mocker.patch(
        'django_north.management.commands.flush.Command.flush')

    call_command('flush')

    assert mock_handle.called is False
    assert mock_flush.called == bool(manage)
