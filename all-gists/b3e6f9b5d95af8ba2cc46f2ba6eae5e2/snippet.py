# based on https://gist.github.com/blueyed/4fb0a807104551f103e6

from django.db import connection
from django.db.migrations.executor import MigrationExecutor

import pytest


@pytest.fixture()
def migration(transactional_db):
    """
    This fixture returns a helper object to test Django data migrations.

    The fixture returns an object with two methods;
     - `before` to initialize db to the state before the migration under test
     - `after` to execute the migration and bring db to the state after the migration

    The methods return `old_apps` and `new_apps` respectively; these can
    be used to initiate the ORM models as in the migrations themselves.

    For example:

        def test_foo_set_to_bar(migration):
            old_apps = migration.before('my_app', '0001_inital')
            Foo = old_apps.get_model('my_app', 'foo')
            Foo.objects.create(bar=False)

            assert Foo.objects.count() == 1
            assert Foo.objects.filter(bar=False).count() == Foo.objects.count()

            # executing migration
            new_apps = migration.apply('my_app', '0002_set_foo_bar')
            Foo = new_apps.get_model('my_app', 'foo')
            assert Foo.objects.filter(bar=False).count() == 0
            assert Foo.objects.filter(bar=True).count() == Foo.objects.count()

    Based on: https://gist.github.com/blueyed/4fb0a807104551f103e6
    """
    class Migrator(object):
        def before(self, app, migrate_from, ):
            """ Specify app and starting migration name as in:
                before('app', '0001_before') => app/migrations/0001_before.py
            """
            self.app = app
            self.migrate_from = [(app, migrate_from)]
            self.executor = MigrationExecutor(connection)
            self.executor.migrate(self.migrate_from)
            # prepare state of db to before the migration ("migrate_from" state)
            self._old_apps = self.executor.loader.project_state(self.migrate_from).apps
            return self._old_apps

        def apply(self, app, migrate_to):
            """ Migrate forwards to the "migrate_to" migration """
            self.migrate_to = [(app, migrate_to)]
            self.executor.loader.build_graph()  # reload.
            self.executor.migrate(self.migrate_to)
            self._new_apps = self.executor.loader.project_state(self.migrate_to).apps
            return self._new_apps

    # ensure to migrate forward migrated apps all the way after test
    def migrate_to_end():
        for _ in range(len(apps)):
            app = apps.pop()
            # migrator.apply(app, '__latest__')
            call_command('migrate', app, verbosity=0)
    request.addfinalizer(migrate_to_end)

    return Migrator()
