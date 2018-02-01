"""Utility for pulling settings from the environment."""
import os
from urllib.parse import urlparse


class EnvParser:
    """Utility for getting settings from the OS environ.

    Instantiate with the name of an env var to get the current mode from (that
    env var should be set to one of VALID_MODES, or not set), then call the
    instantiated parser to parse individual settings from the environ (see
    docstring for ``__call__``).

    """
    VALID_MODES = ['dev', 'prod']
    DEFAULT_MODE = VALID_MODES[0]
    NOT_PROVIDED = object()

    def __init__(self, mode_env_var):
        self.mode = os.environ.get(mode_env_var, self.DEFAULT_MODE)
        if self.mode not in self.VALID_MODES:
            raise ValueError(
                "%s must be one of %s" % (self.mode, self.VALID_MODES))

    def __call__(self, keys, coerce=str, default=NOT_PROVIDED):
        """Utility for getting settings from the OS environ.

        First argument is either a string (an environment variable to get) or a
        list of strings (a list of environment variables, where the first one
        that exists will be used).

        The ``coerce`` argument should be a unary function to convert the
        environment variable's value (which will always be a string) into the
        appropriate Python data type (the default is to leave it as a string).

        The ``default`` argument can be set to a value to use if the given
        environment variable(s) are not found. The ``coerce`` function is still
        applied to the default value, unless the default is ``None``.

        The default can also be a dictionary where the keys are mode names
        (e.g. 'dev', 'prod') and the values are the default to use for that
        mode. If the default is not given (or the default is a dictionary and
        no default is given for the current mode) and the given environment
        variable(s) are not found, ``ValueError`` is raised.

        """
        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            val = os.environ.get(key)
            if val is not None:
                break

        if val is None:
            try:
                default = default.get(self.mode, self.NOT_PROVIDED)
            except AttributeError:  # default is not a dictionary
                pass

            if default is self.NOT_PROVIDED:
                raise ValueError(
                    "Environment variable %r is required." % keys)
            val = default

        return coerce(val) if val is not None else val


def parse_boolean(s):
    """Parse an environment variable string into a boolean.

    Considers empty string, '0', 'no', or 'false' (case insensitive) to be
    ``False``; all other values are ``True``.

    """
    return s.lower() not in {'', '0', 'no', 'false'}


def parse_comma_list(s):
    """Parse comma-separated list in env var to Python list."""
    if not s.strip():
        return []
    return [b.strip() for b in s.split(',')]


def parse_database_url(url):
    """Parse a database URI into a Django db config dictionary.

    Also adds an ``ENGINE`` key: ``django.db.backends.postgresql_psycopg2`` for Postgres. No other
    database is currently supported.

    E.g. parses ``postgres://user:pass@host:port/dbname`` into::

        {
            'NAME': 'dbname',
            'USER': 'user',
            'PASSWORD': 'pass',
            'HOST': 'host',
            'PORT': 'port',
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
        }

    """
    url_parts = urlparse(url)
    return {
        'NAME': url_parts.path[1:],
        'USER': url_parts.username,
        'PASSWORD': url_parts.password,
        'HOST': url_parts.hostname,
        'PORT': url_parts.port,
        'ENGINE': {
            'postgres': 'django.db.backends.postgres',
        }[url_parts.scheme],
    }
