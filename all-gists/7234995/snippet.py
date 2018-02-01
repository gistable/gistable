from south import db as db_module
from south.migration.migrators import Migrator, DryRunMigrator


def with_db(run_migration):

    def run_migration_with_db(self, migration, database):
        migration_db = getattr(migration._migration.Migration,
                               'database', None)
        if migration_db is not None:
            print "Switching to db '%s'" % migration_db
            _pev_db = db_module.db
            db_module.db = db_module.dbs[migration_db]
            migration.migration_instance().db = db_module.db
            database = migration_db
        try:
            run_migration(self, migration, database)
        finally:
            if migration_db is not None:
                print "Switching back to previous db"
                db_module.db = _pev_db
                delattr(migration.migration_instance(), 'db')

    return run_migration_with_db

Migrator.run_migration = with_db(Migrator.run_migration)
DryRunMigrator.run_migration = with_db(DryRunMigrator.run_migration)