
from django.db.utils import ProgrammingError

import pytest

from django_north.management import migrations


def test_get_current_version(settings, mocker):
    mock_comment = mocker.patch(
        'django_north.management.migrations'
        '.get_current_version_from_comment',
        return_value='from_comment')

    # no setting
    if hasattr(settings, 'NORTH_CURRENT_VERSION_DETECTOR'):
        del settings.NORTH_CURRENT_VERSION_DETECTOR

    result = migrations.get_current_version()
    assert mock_comment.called is True
    assert result == 'from_comment'

    # wrong setting
    mock_comment.reset_mock()
    settings.NORTH_CURRENT_VERSION_DETECTOR = (
        'django_north.management.migrations'
        '.get_current_version_from_foo')

    with pytest.raises(AttributeError):
        migrations.get_current_version()
    assert mock_comment.called is False

    # good setting
    mock_comment.reset_mock()
    settings.NORTH_CURRENT_VERSION_DETECTOR = (
        'django_north.management.migrations'
        '.get_current_version_from_comment')

    result = migrations.get_current_version()
    assert mock_comment.called is True
    assert result == 'from_comment'


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
    with pytest.raises(migrations.DBException) as e:
        migrations.get_current_version_from_comment()
    assert 'No comment found on django_site.' in e.value

    # bad comment
    cursor.fetchone.return_value = ['comment']
    with pytest.raises(migrations.DBException) as e:
        migrations.get_current_version_from_comment()
    assert "No version found in django_site's comment." in e.value
    cursor.fetchone.return_value = ['version']
    with pytest.raises(migrations.DBException) as e:
        migrations.get_current_version_from_comment()
    assert "No version found in django_site's comment." in e.value
    cursor.fetchone.return_value = ['version17.01']
    with pytest.raises(migrations.DBException) as e:
        migrations.get_current_version_from_comment()
    assert "No version found in django_site's comment." in e.value

    # correct comment
    cursor.fetchone.return_value = [' version  17.01 ']
    assert migrations.get_current_version_from_comment() == '17.01'
