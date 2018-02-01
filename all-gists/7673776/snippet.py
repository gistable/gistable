import pytest


@pytest.fixture(scope='session')
def _django_db_setup(request, _django_db_setup, _django_cursor_wrapper):
    """Load any data needed for the tests after the database is created.

    This "overwrites" pytest_django's own _django_db_setup.

    """
    with _django_cursor_wrapper:
        if (request.config.getvalue('create_db') or
                not request.config.getvalue('reuse_db')):
            # we're not reusing the database
            #YOUR SETUP HERE, eg: management.call_command('create_categories')

    return _django_db_setup