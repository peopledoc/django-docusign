# -*- coding: utf-8 -*-

from django.apps import apps
from django.core.management.base import BaseCommand

from django_north.management import contenttypes
from django_north.management import permissions


class Command(BaseCommand):
    help = "Displays all the missing fixtures."

    def add_arguments(self, parser):
        parser.add_argument(
            "--unknown-contenttypes", action="store_true",
            dest="unknown_contenttypes", default=False,
            help="Show unknown contenttypes to be removed")

    def handle(self, *args, **options):
        fixtures = []
        if options['unknown_contenttypes']:
            fixtures += self.unknown_contenttypes()
        fixtures += self.missing_contenttypes()
        fixtures += self.missing_permissions()

        return "\n".join(fixtures) + "\n"

    def unknown_contenttypes(self):
        """
        Contenttypes to remove
        """
        cts = []
        for app_config in apps.get_app_configs():
            cts += contenttypes.get_unknown_contenttypes_for_app_config(
                app_config)
        return [
            "DELETE FROM django_content_type "
            "WHERE app_label = '{}' AND model = '{}';".format(
                ct.app_label, ct.model)
            for ct in cts
        ]

    def missing_contenttypes(self):
        """
        Contenttypes to create
        """
        cts = []
        for app_config in apps.get_app_configs():
            cts += contenttypes.get_missing_contenttypes_for_app_config(
                app_config)
        return [
            "INSERT INTO django_content_type(app_label, model) "
            "VALUES('{}', '{}');".format(ct.app_label, ct.model)
            for ct in cts
        ]

    def missing_permissions(self):
        """
        Permissions to create
        """
        perms = []
        for app_config in apps.get_app_configs():
            perms += permissions.get_missing_permissions_for_app_config(
                app_config)
        return [
            "INSERT INTO auth_permission(codename, name, content_type_id) "
            "VALUES('{}', '{}', (SELECT id FROM django_content_type "
            "WHERE app_label = '{}' AND model = '{}'));".format(
                perm.codename, perm.name, perm.content_type.app_label,
                perm.content_type.model)
            for perm in perms
        ]
