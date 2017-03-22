from django.apps import AppConfig
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

import pytest

from django_north.management import contenttypes


class CustomAppConfig(AppConfig):
    path = 'some.path.to.somewhere'


@pytest.mark.django_db
def test_get_all_contenttypes_for_app_config():
    ct1 = ContentType.objects.get(app_label='north_app', model='author')
    ct2 = ContentType.objects.get(app_label='north_app', model='book')
    app_config = apps.get_app_config('north_app')

    result = contenttypes.get_all_contenttypes_for_app_config(app_config)

    assert result == {
        'author': ct1,
        'book': ct2,
    }


def test_get_known_models_for_app_config(mocker):
    model1 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel1'))
    model2 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel2'))
    app_config = CustomAppConfig('myapp', mocker.Mock())

    mocker.patch(
        'django.apps.AppConfig.get_models', return_value=[model1, model2])

    result = contenttypes.get_known_models_for_app_config(app_config)

    assert result == {
        'mymodel1': model1,
        'mymodel2': model2,
    }


def test_get_unknown_contenttypes_for_app_config(mocker):
    ct1 = ContentType(app_label='myapp', model='mymodel1')
    ct2 = ContentType(app_label='myapp', model='mymodel2')
    ct3 = ContentType(app_label='myapp', model='mymodel3')
    model1 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel1'))
    model2 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel2'))
    model4 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel4'))
    app_config = CustomAppConfig('myapp', mocker.Mock())

    mock_get_contenttypes = mocker.patch(
        'django_north.management.contenttypes'
        '.get_all_contenttypes_for_app_config')
    mock_get_models = mocker.patch(
        'django_north.management.contenttypes'
        '.get_known_models_for_app_config')

    # unknown model
    mock_get_contenttypes.return_value = {
        'mymodel1': ct1,
        'mymodel2': ct2,
        'mymodel3': ct3,
    }
    mock_get_models.return_value = {
        'mymodel1': model1,
        'mymodel2': model2,
        'mymodel4': model4,
    }
    result = contenttypes.get_unknown_contenttypes_for_app_config(app_config)
    assert result == [ct3]

    # no unknown model
    mock_get_contenttypes.return_value = {
        'mymodel1': ct1,
        'mymodel2': ct2,
    }
    mock_get_models.return_value = {
        'mymodel1': model1,
        'mymodel2': model2,
        'mymodel4': model4,
    }
    result = contenttypes.get_unknown_contenttypes_for_app_config(app_config)
    assert result == []

    # no models
    mock_get_contenttypes.return_value = {
        'mymodel1': ct1,
        'mymodel2': ct2,
    }
    mock_get_models.return_value = {}
    result = contenttypes.get_unknown_contenttypes_for_app_config(app_config)
    assert result == []

    # no contenttypes
    mock_get_contenttypes.return_value = {}
    mock_get_models.return_value = {
        'mymodel1': model1,
        'mymodel2': model2,
        'mymodel4': model4,
    }
    result = contenttypes.get_unknown_contenttypes_for_app_config(app_config)
    assert result == []


def test_get_missing_contenttypes_for_app_config(mocker):
    ct1 = ContentType(app_label='myapp', model='mymodel1')
    ct2 = ContentType(app_label='myapp', model='mymodel2')
    ct3 = ContentType(app_label='myapp', model='mymodel3')
    model1 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel1'))
    model2 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel2'))
    model4 = mocker.Mock(_meta=mocker.Mock(model_name='mymodel4'))
    app_config = CustomAppConfig('myapp', mocker.Mock())

    mock_get_contenttypes = mocker.patch(
        'django_north.management.contenttypes'
        '.get_all_contenttypes_for_app_config')
    mock_get_models = mocker.patch(
        'django_north.management.contenttypes'
        '.get_known_models_for_app_config')

    # missing contenttype
    mock_get_contenttypes.return_value = {
        'mymodel1': ct1,
        'mymodel2': ct2,
        'mymodel3': ct3,
    }
    mock_get_models.return_value = {
        'mymodel1': model1,
        'mymodel2': model2,
        'mymodel4': model4,
    }
    result = contenttypes.get_missing_contenttypes_for_app_config(app_config)
    assert len(result) == 1
    new_ct = result[0]
    assert new_ct.app_label == 'myapp'
    assert new_ct.model == 'mymodel4'

    # no missing models
    mock_get_contenttypes.return_value = {
        'mymodel1': ct1,
        'mymodel2': ct2,
        'mymodel3': ct3,
    }
    mock_get_models.return_value = {
        'mymodel1': model1,
        'mymodel2': model2,
    }
    result = contenttypes.get_missing_contenttypes_for_app_config(app_config)
    assert result == []

    # no models
    mock_get_contenttypes.return_value = {
        'mymodel1': ct1,
        'mymodel2': ct2,
    }
    mock_get_models.return_value = {}
    result = contenttypes.get_missing_contenttypes_for_app_config(app_config)
    assert result == []

    # no contenttypes
    mock_get_contenttypes.return_value = {}
    mock_get_models.return_value = {
        'mymodel1': model1,
        'mymodel2': model2,
        'mymodel4': model4,
    }
    result = contenttypes.get_missing_contenttypes_for_app_config(app_config)
    result.sort(key=lambda ct: ct.model)
    assert len(result) == 3
    new_ct = result[0]
    assert new_ct.app_label == 'myapp'
    assert new_ct.model == 'mymodel1'
    new_ct = result[1]
    assert new_ct.app_label == 'myapp'
    assert new_ct.model == 'mymodel2'
    new_ct = result[2]
    assert new_ct.app_label == 'myapp'
    assert new_ct.model == 'mymodel4'
