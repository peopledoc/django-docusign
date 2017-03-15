# -*- coding: utf-8 -*-
import io
import logging
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from django_north.management import migrations
from django_north.management.runner import Script

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate the DB to the target version."

    def handle(self, *args, **options):
        if getattr(settings, 'NORTH_MANAGE_DB', False) is not True:
            logger.info('migrate command disabled')
            return

        self.verbosity = options.get('verbosity')

        self.migrate()

    def migrate(self):
        # build miration plan
        migration_plan = migrations.build_migration_plan()

        if migration_plan is None:
            # schema not inited
            self.init_schema()
            # reload migration_plan
            migration_plan = migrations.build_migration_plan()

        # play migrations
        recorder = migrations.MigrationRecorder(connection)
        for plan in migration_plan['plans']:
            version = plan['version']
            if self.verbosity >= 1:
                self.stdout.write(self.style.MIGRATE_LABEL(version))
            for mig, applied, path in plan['plan']:
                title = mig
                if '/manual/' in path:
                    title += ' (manual)'
                if applied:
                    if self.verbosity >= 1:
                        self.stdout.write("  {} already applied".format(title))
                else:
                    if self.verbosity >= 1:
                        self.stdout.write("  Applying {}...".format(title))
                    self.run_script(path)
                    recorder.record_applied(version, mig)

    def init_schema(self):
        init_version = migrations.get_version_for_init()

        # load additional files
        additional_files = getattr(
            settings, 'NORTH_ADDITIONAL_SCHEMA_FILES', [])
        for file_name in additional_files:
            file_path = os.path.join(
                settings.NORTH_MIGRATIONS_ROOT, 'schemas', file_name)
            if self.verbosity >= 1:
                self.stdout.write(
                    self.style.MIGRATE_LABEL("Load {}".format(file_name)))
            self.run_script(file_path)

        # load schema
        if self.verbosity >= 1:
            self.stdout.write(self.style.MIGRATE_LABEL("Load schema"))
            self.stdout.write("  Applying {}...".format(init_version))
        schema_path = os.path.join(
            settings.NORTH_MIGRATIONS_ROOT,
            'schemas',
            getattr(settings, 'NORTH_SCHEMA_TPL',
                    migrations.schema_default_tpl)
            .format(init_version))
        self.run_script(schema_path)

        # load fixtures
        if self.verbosity >= 1:
            self.stdout.write(self.style.MIGRATE_LABEL("Load fixtures"))
            self.stdout.write("  Applying {}...".format(init_version))
        fixtures_path = os.path.join(
            settings.NORTH_MIGRATIONS_ROOT,
            'fixtures',
            getattr(settings, 'NORTH_FIXTURES_TPL',
                    migrations.fixtures_default_tpl)
            .format(init_version))
        self.run_script(fixtures_path)

    def run_script(self, path):
        with io.open(path, 'r', encoding='utf8') as f:
            script = Script(f)
            script.run(connection)
