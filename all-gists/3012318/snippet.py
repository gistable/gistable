from optparse import make_option

from django.test.simple import DjangoTestSuiteRunner


def fake_create_test_db(self, verbosity=1, autoclobber=False):
    """Simplified version of BaseDatabaseCreation.create_test_db."""
    test_database_name = self._get_test_db_name()

    if verbosity >= 1:
        test_db_repr = ''
        if verbosity >= 2:
            test_db_repr = " ('%s')" % test_database_name
        print "Using existing test database for alias '%s'%s..." % (self.connection.alias, test_db_repr)

    self.connection.close()
    self.connection.settings_dict["NAME"] = test_database_name

    # Confirm the feature set of the test database
    self.connection.features.confirm()

    # Get a cursor (even though we don't need one yet). This has
    # the side effect of initializing the test database.
    self.connection.cursor()

    return test_database_name


def fake_destroy_test_db(self, old_database_name, verbosity=1):
    """Simplified version of BaseDatabaseCreation.destroy_test_db."""
    self.connection.close()
    test_database_name = self.connection.settings_dict['NAME']
    if verbosity >= 1:
        test_db_repr = ''
        if verbosity >= 2:
            test_db_repr = " ('%s')" % test_database_name
        print "Preserving test database for alias '%s'%s..." % (self.connection.alias, test_db_repr)
    self.connection.settings_dict['NAME'] = old_database_name


class AutoslaveTestSuiteRunner(DjangoTestSuiteRunner):

    option_list = (
        make_option('--createdb',
            action='store_true', dest='createdb', default=False,
            help='Create, or re-create, the test database before the tests. '
                 'Use this one the first run and when your models change.'),
        make_option('--dropdb',
            action='store_true', dest='dropdb', default=False,
            help='Drop the test database after the tests.'),
    )

    def __init__(self, createdb=True, dropdb=True, **kwargs):
        self.createdb = createdb
        self.dropdb = dropdb
        super(AutoslaveTestSuiteRunner, self).__init__(**kwargs)

    def setup_databases(self, **kwargs):
        """Create the test databases only when explicitly requested.

        Also create initial data for some models. We can't use 'initial_data'
        fixtures for objects whose contents may be edited in production,
        because they would be overwritten by updates.
        """
        if not self.createdb:
            from django.db.backends.creation import BaseDatabaseCreation
            BaseDatabaseCreation.create_test_db = fake_create_test_db

        result = super(AutoslaveTestSuiteRunner, self).setup_databases(**kwargs)
        if self.createdb:
            # Initialize some tables that are populated by scripts
            # rather than fixtures; hardcoded for our local setup.
            pass
        return result

    def teardown_databases(self, old_config, **kwargs):
        """Drop the test databases only when explicitly requested."""
        if not self.dropdb:
            from django.db.backends.creation import BaseDatabaseCreation
            BaseDatabaseCreation.destroy_test_db = fake_destroy_test_db