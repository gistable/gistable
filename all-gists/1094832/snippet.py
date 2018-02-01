"""
sqlite3 database backend with non-synchronous mode.

It gives you a huge performance boost by turning off the overzealous
synchronous operation mode. The tradeoff is less data protection in case of
power outages but come on, you were not going to use it in production, were you?
"""
from django.db.backends.sqlite3.base import (
    DatabaseWrapper as Sqlite3Wrapper,
    DatabaseError,
    IntegrityError,
    DatabaseFeatures,
    DatabaseOperations,
)

__all__ = ['DatabaseWrapper', 'DatabaseError', 'IntegrityError',
           'DatabaseFeatures', 'DatabaseOperations']

class DatabaseWrapper(Sqlite3Wrapper):
    def _cursor(self):
        new_conn = self.connection is None
        cur = super(DatabaseWrapper, self)._cursor()
        if new_conn:
            cur.execute('PRAGMA synchronous=OFF')
        return cur