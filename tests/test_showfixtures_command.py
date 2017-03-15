from django.apps import AppConfig
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.utils.six import StringIO

from django_north.management.commands import showfixtures


class CustomAppConfig(AppConfig):
    path = 'some.path.to.somewhere'


def test_unknown_contenttypes(mocker):
    ct1 = ContentType(app_label='myapp1', model='mymodel1', id=1)
    ct2 = ContentType(app_label='myapp1', model='mymodel2', id=2)
    ct3 = ContentType(app_label='myapp2', model='mymodel3', id=3)
    app_config1 = CustomAppConfig('myapp1', mocker.Mock())
    app_config2 = CustomAppConfig('myapp2', mocker.Mock())
    app_config3 = CustomAppConfig('myapp3', mocker.Mock())
    mocker.patch(
        'django_north.management.commands.showfixtures.apps'
        '.get_app_configs',
        return_value=[app_config1, app_config2, app_config3])
    mock_get_contenttypes = mocker.patch(
        'django_north.management.contenttypes'
        '.get_unknown_contenttypes_for_app_config')

    command = showfixtures.Command()

    # unknown contenttypes
    mock_get_contenttypes.side_effect = [
        [ct1, ct2],
        [ct3],
        []]
    assert command.unknown_contenttypes() == [
        "DELETE FROM django_content_type "
        "WHERE app_label = 'myapp1' AND model = 'mymodel1';",
        "DELETE FROM django_content_type "
        "WHERE app_label = 'myapp1' AND model = 'mymodel2';",
        "DELETE FROM django_content_type "
        "WHERE app_label = 'myapp2' AND model = 'mymodel3';",
    ]

    # no unknown contenttypes
    mock_get_contenttypes.side_effect = [[], [], []]
    assert command.unknown_contenttypes() == []


def test_missing_contenttypes(mocker):
    ct1 = ContentType(app_label='myapp1', model='mymodel1')
    ct2 = ContentType(app_label='myapp1', model='mymodel2')
    ct3 = ContentType(app_label='myapp2', model='mymodel3')
    app_config1 = CustomAppConfig('myapp1', mocker.Mock())
    app_config2 = CustomAppConfig('myapp2', mocker.Mock())
    app_config3 = CustomAppConfig('myapp3', mocker.Mock())
    mocker.patch(
        'django_north.management.commands.showfixtures.apps'
        '.get_app_configs',
        return_value=[app_config1, app_config2, app_config3])
    mock_get_contenttypes = mocker.patch(
        'django_north.management.contenttypes'
        '.get_missing_contenttypes_for_app_config')

    command = showfixtures.Command()

    # missing contenttypes
    mock_get_contenttypes.side_effect = [
        [ct1, ct2],
        [ct3],
        []]
    assert command.missing_contenttypes() == [
        "INSERT INTO django_content_type(app_label, model) "
        "VALUES('myapp1', 'mymodel1');",
        "INSERT INTO django_content_type(app_label, model) "
        "VALUES('myapp1', 'mymodel2');",
        "INSERT INTO django_content_type(app_label, model) "
        "VALUES('myapp2', 'mymodel3');"
    ]

    # no missing contenttypes
    mock_get_contenttypes.side_effect = [[], [], []]
    assert command.missing_contenttypes() == []


def test_missing_permissions(mocker):
    ct1 = ContentType(app_label='myapp1', model='mymodel1', id=1)
    ct2 = ContentType(app_label='myapp1', model='mymodel2', id=2)
    p1 = Permission(codename='perm1', name='Perm1', content_type=ct1)
    p2 = Permission(codename='perm2', name='Perm2', content_type=ct1)
    p3 = Permission(codename='perm3', name='Perm3', content_type=ct2)
    app_config1 = CustomAppConfig('myapp1', mocker.Mock())
    app_config2 = CustomAppConfig('myapp2', mocker.Mock())
    app_config3 = CustomAppConfig('myapp3', mocker.Mock())
    mocker.patch(
        'django_north.management.commands.showfixtures.apps'
        '.get_app_configs',
        return_value=[app_config1, app_config2, app_config3])
    mock_get_permissions = mocker.patch(
        'django_north.management.permissions'
        '.get_missing_permissions_for_app_config')

    command = showfixtures.Command()

    # missing permissions
    mock_get_permissions.side_effect = [
        [p1, p2],
        [p3],
        []]
    assert command.missing_permisions() == [
        "INSERT INTO auth_permission(codename, name, content_type_id) "
        "VALUES('perm1', 'Perm1', (SELECT id FROM django_content_type "
        "WHERE app_label = 'myapp1' AND model = 'mymodel1'));",
        "INSERT INTO auth_permission(codename, name, content_type_id) "
        "VALUES('perm2', 'Perm2', (SELECT id FROM django_content_type "
        "WHERE app_label = 'myapp1' AND model = 'mymodel1'));",
        "INSERT INTO auth_permission(codename, name, content_type_id) "
        "VALUES('perm3', 'Perm3', (SELECT id FROM django_content_type "
        "WHERE app_label = 'myapp1' AND model = 'mymodel2'));",
    ]

    # no missing permissions
    mock_get_permissions.side_effect = [[], [], []]
    assert command.missing_permisions() == []


def test_showfixtures(mocker):
    mocker.patch(
        'django_north.management.commands.showfixtures.Command'
        '.unknown_contenttypes',
        return_value=['DELETE 1', 'DELETE 2', 'DELETE 3'])
    mocker.patch(
        'django_north.management.commands.showfixtures.Command'
        '.missing_contenttypes',
        return_value=['INSERT 1', 'INSERT 2', 'INSERT 3'])
    mocker.patch(
        'django_north.management.commands.showfixtures.Command'
        '.missing_permisions',
        return_value=['INSERT 4', 'INSERT 5', 'INSERT 6'])

    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    call_command('showfixtures')
    assert stdout.getvalue() == (
        'INSERT 1\nINSERT 2\nINSERT 3\n'
        'INSERT 4\nINSERT 5\nINSERT 6\n')

    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    call_command('showfixtures', unknown_contenttypes=True)
    assert stdout.getvalue() == (
        'DELETE 1\nDELETE 2\nDELETE 3\n'
        'INSERT 1\nINSERT 2\nINSERT 3\n'
        'INSERT 4\nINSERT 5\nINSERT 6\n')
