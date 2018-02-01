from django.test.simple import DjangoTestSuiteRunner

class ByPassableDBDjangoTestSuiteRunner(DjangoTestSuiteRunner):

    def setup_databases(self, **kwargs):
        from django.db import connections
        old_names = []
        mirrors = []
        for alias in connections:
            connection = connections[alias]
            # If the database is a test mirror, redirect it's connection
            # instead of creating a test database.
            if connection.settings_dict['TEST_MIRROR']:
                mirrors.append((alias, connection))
                mirror_alias = connection.settings_dict['TEST_MIRROR']
                connections._connections[alias] = connections[mirror_alias]
            elif connection.settings_dict.get('BYPASS_CREATION','no') == 'no':
                old_names.append((connection, connection.settings_dict['NAME']))
                connection.creation.create_test_db(self.verbosity, autoclobber=not self.interactive)
        return old_names, mirrors