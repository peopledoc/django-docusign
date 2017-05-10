from __future__ import unicode_literals

import io
import logging
import os
import sys
from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.core.management.color import no_style
from django.core.management.sql import sql_flush
from django.db import DEFAULT_DB_ALIAS
from django.db import connections
from django.db import transaction
from django.utils import six
from django.utils.six.moves import input

from django_north.management.migrations import get_current_version
from django_north.management.migrations import get_fixtures_for_init
from django_north.management.migrations import fixtures_default_tpl
from django_north.management.runner import Script

logger = logging.getLogger(__name__)


# warning: backport from django 1.8
# this command changed a lot in 1.10


class Command(BaseCommand):
    help = ('Removes ALL DATA from the database, including data added during '
            'migrations. Unmigrated apps will also have their initial_data '
            'fixture reloaded. Does not achieve a "fresh install" state.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', action='store_false', dest='interactive',
            default=True,
            help='Tells Django to NOT prompt the user for input of any kind.')
        parser.add_argument(
            '--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to flush. Defaults to the "default" '
            'database.')
        parser.add_argument(
            '--no-initial-data', action='store_false',
            dest='load_initial_data', default=True,
            help='Tells Django not to load any initial data after database '
            'synchronization.')

    def handle(self, **options):
        if getattr(settings, 'NORTH_MANAGE_DB', False) is not True:
            logger.info('flush command disabled')
            return

        self.flush(**options)

    def flush(self, **options):
        database = options.get('database')
        connection = connections[database]
        verbosity = options.get('verbosity')
        interactive = options.get('interactive')
        # The following are stealth options used by Django's internals.
        reset_sequences = options.get('reset_sequences', True)
        allow_cascade = options.get('allow_cascade', False)
        inhibit_post_migrate = options.get('inhibit_post_migrate', False)

        self.style = no_style()

        # Import the 'management' module within each installed app, to register
        # dispatcher events.
        for app_config in apps.get_app_configs():
            try:
                import_module('.management', app_config.name)
            except ImportError:
                pass

        # custom: only_django False
        # get current version before flush
        current_version = get_current_version()
        sql_list = sql_flush(self.style, connection, only_django=False,
                             reset_sequences=reset_sequences,
                             allow_cascade=allow_cascade)

        if interactive:
            confirm = input(
                """You have requested a flush of the database.
This will IRREVERSIBLY DESTROY all data currently in the %r database,
and return each table to an empty state.
Are you sure you want to do this?

    Type 'yes' to continue, or 'no' to cancel: """
                % connection.settings_dict['NAME'])
        else:
            confirm = 'yes'

        if confirm == 'yes':
            try:
                with transaction.atomic(
                        using=database,
                        savepoint=connection.features.can_rollback_ddl):
                    with connection.cursor() as cursor:
                        for sql in sql_list:
                            cursor.execute(sql)
            except Exception as e:
                new_msg = (
                    "Database %s couldn't be flushed. Possible reasons:\n"
                    "  * The database isn't running or isn't configured "
                    "correctly.\n"
                    "  * At least one of the expected database tables doesn't "
                    "exist.\n"
                    "  * The SQL was invalid.\n"
                    "Hint: Look at the output of 'django-admin sqlflush'. "
                    "That's the SQL this command wasn't able to run.\n"
                    "The full error: %s") % (
                        connection.settings_dict['NAME'], e)
                six.reraise(
                    CommandError, CommandError(new_msg), sys.exc_info()[2])

            if not inhibit_post_migrate:
                self.emit_post_migrate(
                    verbosity, interactive, database, current_version)

            # Reinstall the initial_data fixture.
            if options.get('load_initial_data'):
                # Reinstall the initial_data fixture for apps without
                # migrations.
                from django.db.migrations.executor import MigrationExecutor
                executor = MigrationExecutor(connection)
                app_options = options.copy()
                for app_label in executor.loader.unmigrated_apps:
                    app_options['app_label'] = app_label
                    try:
                        call_command('loaddata', 'initial_data', **app_options)
                    except CommandError:
                        # fails with django 1.10 if initial_data does not exist
                        pass
        else:
            self.stdout.write("Flush cancelled.\n")

    @staticmethod
    def emit_post_migrate(verbosity, interactive, database, current_version):
        # custom: do what was done on post_migrate
        # clear contenttype cache
        ContentType.objects.clear_cache()

        # reload fixtures
        connection = connections[database]
        fixtures_version = get_fixtures_for_init(current_version)
        fixtures_path = os.path.join(
            settings.NORTH_MIGRATIONS_ROOT,
            'fixtures',
            getattr(settings, 'NORTH_FIXTURES_TPL', fixtures_default_tpl)
            .format(fixtures_version))
        with io.open(fixtures_path, 'r', encoding='utf8') as f:
            script = Script(f)
            script.run(connection)
