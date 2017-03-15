from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS
from django.utils import six


def get_all_contenttypes_for_app_config(app_config, using=DEFAULT_DB_ALIAS):
    """
    Return all existing contenttypes for a given app_config
    """
    app_label = app_config.label

    return {
        ct.model: ct
        for ct in ContentType.objects.using(using).filter(app_label=app_label)
    }


def get_known_models_for_app_config(app_config):
    """
    Return all known models for a given app config
    """
    return {
        model._meta.model_name: model
        for model in app_config.get_models()}


def get_unknown_contenttypes_for_app_config(app_config):
    """
    Return unknown contenttypes for a given app_config
    """
    app_models = get_known_models_for_app_config(app_config)
    if not app_models:
        return []

    content_types = get_all_contenttypes_for_app_config(app_config)
    if not content_types:
        return []

    return [
        ct
        for (model_name, ct) in six.iteritems(content_types)
        if model_name not in app_models
    ]


def get_missing_contenttypes_for_app_config(app_config):
    """
    Return missing contenttypes for a given app_config
    """
    app_label = app_config.label

    app_models = get_known_models_for_app_config(app_config)
    if not app_models:
        return []

    content_types = get_all_contenttypes_for_app_config(app_config)

    return [
        ContentType(
            app_label=app_label,
            model=model_name,
        )
        for (model_name, model) in six.iteritems(app_models)
        if model_name not in content_types
    ]
