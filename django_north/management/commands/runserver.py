# -*- coding: utf-8 -*-
from django.contrib.staticfiles.management.commands.runserver import \
    Command as RunserverCommand

from django_north.management import migrations


class Command(RunserverCommand):
    help = ("Starts a lightweight Web server for development and also "
            "serves static files.")

    def check_migrations(self):
        try:
            migration_plan = migrations.build_migration_plan()
        except migrations.DBException as e:
            self.stdout.write(self.style.NOTICE("\n{}\n".format(e)))
            return

        if migration_plan is None:
            self.stdout.write(self.style.NOTICE("\nSchema not inited.\n"))
            return

        has_migrations = any(
            [
                any([not applied for mig, applied, path in plan['plan']])
                for plan in migration_plan['plans']
            ]
        )
        if has_migrations:
            self.stdout.write(self.style.NOTICE(
                "\nYou have unapplied migrations; your app may not work "
                "properly until they are applied."
            ))
            self.stdout.write(self.style.NOTICE(
                "Run 'python manage.py migrate' to apply them.\n"
            ))
