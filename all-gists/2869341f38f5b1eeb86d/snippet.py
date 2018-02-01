# If your test settings file doesn't import any other settings file
# then you can use the function directly:

def prevent_tests_migrate(db):
    import django
    from django.db import connections
    from django.db.migrations.executor import MigrationExecutor
    django.setup()
    ma = MigrationExecutor(connections[db]).loader.migrated_apps
    return dict(zip(ma, ['{a}.notmigrations'.format(a=a) for a in ma]))
MIGRATION_MODULES = prevent_tests_migrate('default')

# If your test settings file imports another settings file (typically
# your base settings file, then the function won't work as the settings
# won't be fully in scope by the time setup() is called. Depending on
# you settings layout you'll an error like:
# "ImproperlyConfigured: The SECRET_KEY setting must not be empty."
# or ""Apps aren't loaded yet", or "RuntimeError: populate() isn't reentrant"
#
# Instead, simply use the function in the Django shell to generate the
# dictionary and hardcode it to MIGRATION_MODULES in the test settings.
# Since Django is already set up in the shell the function can just be:
def prevent_tests_migrate(db):
    from django.db import connections
    from django.db.migrations.executor import MigrationExecutor
    ma = MigrationExecutor(connections[db]).loader.migrated_apps
    return dict(zip(ma, ['{a}.notmigrations'.format(a=a) for a in ma]))

# You'll need to manually update MIGRATION_MODULES if you add new apps
# with migrations and want them skipped as well.
#
# Also, if you suddenly come across an error like this when Django starts up:
# "Migration foo.0001_initial dependencies reference nonexistent
# parent node (u'bar', u'0001_initial')"
# then it probably means you've added an app (maybe 3rd party) that has a
# dependency on one of the apps in MIGRATION_MODULES that you've skipped
# (e.g. a dependency on the contenttypes app). To fix, simply add the new
# app to MIGRATION_MODULES.

