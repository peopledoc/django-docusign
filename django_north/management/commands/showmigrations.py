# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from django_north.management import migrations

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Shows all available migrations for the current project"

    def handle(self, *args, **options):
        if getattr(settings, 'NORTH_MANAGE_DB', False) is not True:
            logger.info('showmigrations command disabled')
            return

        return self.show_list()

    def show_list(self):
        """
        Shows a list of all migrations on the system,
        from the version used to init the DB, to the current target version.
        """
        migration_plan = migrations.build_migration_plan()
        if migration_plan is None:
            self.stdout.write(self.style.ERROR("Schema not inited"))
            return

        self.stdout.write(
            self.style.MIGRATE_HEADING("Current version of the DB:"))
        self.stdout.write(
            self.style.MIGRATE_LABEL(
                "  {}".format(migration_plan['current_version'])))

        self.stdout.write(
            self.style.MIGRATE_HEADING("Schema used to init the DB:"))
        self.stdout.write(
            self.style.MIGRATE_LABEL(
                "  {}".format(migration_plan['init_version'])))

        # display migration status for each version to apply
        for plan in migration_plan['plans']:
            self.stdout.write(self.style.MIGRATE_HEADING("Version:"))
            self.stdout.write(
                self.style.MIGRATE_LABEL("  {}".format(plan['version'])))
            # print plan
            for mig, applied, path in plan['plan']:
                title = mig
                if '/manual/' in path:
                    title += ' (manual)'
                if applied:
                    self.stdout.write("  [X] %s" % title)
                else:
                    self.stdout.write("  [ ] %s" % title)
