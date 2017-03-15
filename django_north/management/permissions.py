from django.contrib.auth.management import _get_all_permissions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS


def get_all_contenttypes_for_app_config(app_config, using=DEFAULT_DB_ALIAS):
    """
    Return all contenttypes tht already exists for a given app_config
    """
    ctypes = list()
    for klass in app_config.get_models():
        opts = ContentType.objects._get_opts(klass, True)
        try:
            ctype = ContentType.objects.db_manager(using).get(
                app_label=opts.app_label, model=opts.model_name)
            ctypes.append((ctype, klass))
        except ContentType.DoesNotExist:
            continue
    return ctypes


def get_searched_permissions(ctypes):
    """
    Return all permissions that should exist for existing contenttypes
    """
    # This will hold the permissions we're looking for as
    # (content_type, (codename, name))
    searched_perms = list()
    for ctype, klass in ctypes:
        for perm in _get_all_permissions(klass._meta, ctype):
            searched_perms.append((ctype, perm))

    return searched_perms


def get_all_permissions(ctypes, using=DEFAULT_DB_ALIAS):
    """
    Return all existing permissions for existing contenttypes
    """
    # Find all the Permissions that have a content_type for a model we're
    # looking for.  We don't need to check for codenames since we already have
    # a list of the ones we're going to create.
    return set(Permission.objects.using(using).filter(
        content_type__in=ctypes,
    ).values_list(
        "content_type", "codename"
    ))


def get_missing_permissions_for_app_config(app_config):
    """
    Return missing permissions for a given app config
    """
    # get existing contenttypes
    ctypes = get_all_contenttypes_for_app_config(app_config)
    if not ctypes:
        return []

    # get all permissions that should exist
    searched_perms = get_searched_permissions(ctypes)
    if not searched_perms:
        return []

    # get existing permissions
    all_perms = get_all_permissions([ctype for ctype, klass in ctypes])

    # build missing permissions
    perms = [
        Permission(codename=codename, name=name, content_type=ct)
        for ct, (codename, name) in searched_perms
        if (ct.pk, codename) not in all_perms
    ]

    return perms
