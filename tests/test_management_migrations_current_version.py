
from django.db.utils import ProgrammingError

import pytest

from django_north.management import migrations


def test_get_current_version(settings, mocker):
    mock_table = mocker.patch(
        'django_north.management.migrations'
        '.get_current_version_from_table',
        return_value='from_table')
    mock_comment = mocker.patch(
        'django_north.management.migrations'
        '.get_current_version_from_comment',
        return_value='from_comment')

    # no setting
    if hasattr(settings, 'NORTH_CURRENT_VERSION_DETECTOR'):
        del settings.NORTH_CURRENT_VERSION_DETECTOR

    result = migrations.get_current_version()
    assert mock_table.called is True
    assert mock_comment.called is False
    assert result == 'from_table'

    # wrong setting
    mock_table.reset_mock()
    mock_comment.reset_mock()
    settings.NORTH_CURRENT_VERSION_DETECTOR = (
        'django_north.management.migrations'
        '.get_current_version_from_foo')

    with pytest.raises(AttributeError):
        migrations.get_current_version()
    assert mock_table.called is False
    assert mock_comment.called is False

    # good setting - table
    mock_table.reset_mock()
    mock_comment.reset_mock()
    settings.NORTH_CURRENT_VERSION_DETECTOR = (
        'django_north.management.migrations'
        '.get_current_version_from_table')

    result = migrations.get_current_version()
    assert mock_table.called is True
    assert mock_comment.called is False
    assert result == 'from_table'

    # good setting - comment
    mock_table.reset_mock()
    mock_comment.reset_mock()
    settings.NORTH_CURRENT_VERSION_DETECTOR = (
        'django_north.management.migrations'
        '.get_current_version_from_comment')

    result = migrations.get_current_version()
    assert mock_table.called is False
    assert mock_comment.called is True
    assert result == 'from_comment'


def test_get_current_version_from_table(mocker):
    cursor = mocker.MagicMock()
    mock_cursor = mocker.patch('django.db.connection.cursor')
    mock_cursor.return_value.__enter__.return_value = cursor

    # table does not exist
    cursor.execute.side_effect = ProgrammingError
    assert migrations.get_current_version_from_table() is None

    cursor.execute.side_effect = None

    # no entries
    cursor.fetchall.return_value = []
    assert migrations.get_current_version_from_table() is None

    # many entries
    cursor.fetchall.return_value = [('16.9',), ('foo',), ('17.1',), ('17.02',)]
    assert migrations.get_current_version_from_table() == '17.02'


def test_get_current_version_from_comment(mocker):
    cursor = mocker.MagicMock()
    mock_cursor = mocker.patch('django.db.connection.cursor')
    mock_cursor.return_value.__enter__.return_value = cursor

    # table does not exist
    cursor.execute.side_effect = ProgrammingError
    assert migrations.get_current_version_from_comment() is None

    cursor.execute.side_effect = None

    # no comment
    cursor.fetchone.return_value = [None]
    message = "No comment found on django_site."
    with pytest.raises(migrations.DBException, message=message):
        migrations.get_current_version_from_comment()

    # bad comment
    cursor.fetchone.return_value = ['comment']
    message = "No version found in django_site's comment."
    with pytest.raises(migrations.DBException, message=message):
        migrations.get_current_version_from_comment()
    cursor.fetchone.return_value = ['version']
    with pytest.raises(migrations.DBException, message=message):
        migrations.get_current_version_from_comment()
    cursor.fetchone.return_value = ['version17.01']
    with pytest.raises(migrations.DBException, message=message):
        migrations.get_current_version_from_comment()

    # correct comment
    cursor.fetchone.return_value = [' version  17.01 ']
    assert migrations.get_current_version_from_comment() == '17.01'
