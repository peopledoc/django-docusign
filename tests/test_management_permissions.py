from django.apps import AppConfig
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

import pytest

from django_north.management import permissions


class CustomAppConfig(AppConfig):
    path = 'some.path.to.somewhere'


def test_get_all_contenttypes_for_app_config(mocker):
    model1 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel1'))
    model2 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel2'))
    ct1 = ContentType(app_label='myapp', model='mymodel1')
    ct2 = ContentType(app_label='myapp', model='mymodel2')
    app_config = CustomAppConfig('myapp', mocker.Mock())

    mocker.patch(
        'django.apps.AppConfig.get_models', return_value=[model1, model2])
    mock_get_for_model = mocker.patch(
        'django.contrib.contenttypes.models.ContentTypeManager.get')

    mock_get_for_model.side_effect = [ct1, ct2]
    result = permissions.get_all_contenttypes_for_app_config(app_config)

    assert result == [(ct1, model1), (ct2, model2)]

    mock_get_for_model.side_effect = [ct1, ContentType.DoesNotExist]
    result = permissions.get_all_contenttypes_for_app_config(app_config)

    assert result == [(ct1, model1)]


@pytest.mark.django_db
def test_get_all_permissions():
    bad_ct = ContentType.objects.create(
        app_label='myapp', model='mymodel1')
    Permission.objects.create(
        content_type=bad_ct, codename='badcodename', name='bad name')
    ct1 = ContentType.objects.get(app_label='north_app', model='author')
    ct2 = ContentType.objects.get(app_label='north_app', model='book')

    result = permissions.get_all_permissions([ct1, ct2])
    assert result == set([
        (ct2.pk, u'change_book'), (ct2.pk, u'delete_book'),
        (ct2.pk, u'add_book'),
        (ct1.pk, u'change_author'), (ct1.pk, u'add_author'),
        (ct1.pk, u'delete_author'),
    ])

    result = permissions.get_all_permissions([ct1])
    assert result == set([
        (ct1.pk, u'change_author'), (ct1.pk, u'delete_author'),
        (ct1.pk, u'add_author'),
    ])

    Permission.objects.get(codename='delete_author').delete()
    result = permissions.get_all_permissions([ct1])
    assert result == set([
        (ct1.pk, u'change_author'), (ct1.pk, u'add_author'),
    ])


def test_get_searched_permissions(mocker):
    ct1 = ContentType(app_label='myapp', model='mymodel1')
    ct2 = ContentType(app_label='myapp', model='mymodel2')
    model1 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel1'))
    model2 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel2'))

    perms = [
        [('add_mymodel1', 'Can add Mymodel1'),
         ('change_mymodel1', 'Can change Mymodel1'),
         ('delete_mymodel1', 'Can delete Mymodel1')],
        [('add_mymodel2', 'Can add Mymodel2'),
         ('change_mymodel2', 'Can change Mymodel2'),
         ('delete_mymodel2', 'Can delete Mymodel2'),
         ('custom', 'Custom')]
    ]
    mocker.patch(
        'django_north.management.permissions._get_all_permissions',
        side_effect=perms)
    result = permissions.get_searched_permissions(
        [(ct1, model1), (ct2, model2)])

    assert result == [
        (ct1, perms[0][0]),
        (ct1, perms[0][1]),
        (ct1, perms[0][2]),
        (ct2, perms[1][0]),
        (ct2, perms[1][1]),
        (ct2, perms[1][2]),
        (ct2, perms[1][3]),
    ]


def test_get_missing_permissions_for_app_config(mocker):
    ct1 = ContentType(app_label='myapp', model='mymodel1', id=1)
    ct2 = ContentType(app_label='myapp', model='mymodel2', id=2)
    model1 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel1'))
    model2 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel2'))
    app_config = CustomAppConfig('myapp', mocker.Mock())

    mock_get_contenttypes = mocker.patch(
        'django_north.management.permissions'
        '.get_all_contenttypes_for_app_config')
    mock_get_searched_perms = mocker.patch(
        'django_north.management.permissions'
        '.get_searched_permissions')
    mock_get_all_perms = mocker.patch(
        'django_north.management.permissions.get_all_permissions')

    # missing permissions
    mock_get_contenttypes.return_value = [(ct1, model1), (ct2, model2)]
    mock_get_searched_perms.return_value = [
        (ct1, ('perm11', 'Perm11')),
        (ct1, ('perm12', 'Perm12')),
        (ct2, ('perm2', 'Perm2')),
    ]
    mock_get_all_perms.return_value = [
        (1, 'perm11'),
        (2, 'perm2'),
    ]
    result = permissions.get_missing_permissions_for_app_config(app_config)
    assert len(result) == 1
    new_perm = result[0]
    assert new_perm.codename == 'perm12'
    assert new_perm.name == 'Perm12'
    assert new_perm.content_type == ct1

    # no existing contenttypes
    mock_get_contenttypes.return_value = []
    mock_get_searched_perms.return_value = [
        (ct1, ('perm11', 'Perm11')),
        (ct1, ('perm12', 'Perm12')),
        (ct2, ('perm2', 'Perm2')),
    ]
    mock_get_all_perms.return_value = [
        (1, 'perm11'),
        (2, 'perm2'),
    ]
    result = permissions.get_missing_permissions_for_app_config(app_config)
    assert result == []

    # no searched perms
    mock_get_contenttypes.return_value = [(ct1, model1), (ct2, model2)]
    mock_get_searched_perms.return_value = []
    mock_get_all_perms.return_value = [
        (1, 'perm11'),
        (2, 'perm2'),
    ]
    result = permissions.get_missing_permissions_for_app_config(app_config)
    assert result == []
