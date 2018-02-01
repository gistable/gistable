"""
SQLAlchemy, PostgreSQL (psycopg2), and autocommit

See blog post: http://oddbird.net/2014/06/14/sqlalchemy-postgres-autocommit/

"""
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session as BaseSession


class Session(BaseSession):
    def __init__(self, *a, **kw):
        super(Session, self).__init__(*a, **kw)
        self._in_atomic = False

    @contextmanager
    def atomic(self):
        """Transaction context manager.

        Will commit the transaction on successful completion of the block, or
        roll it back on error.

        Supports nested usage (via savepoints).

        """
        nested = self._in_atomic
        self.begin(nested=nested)
        self._in_atomic = True

        try:
            yield
        except:
            self.rollback()
            raise
        else:
            self.commit()
        finally:
            if not nested:
                self._in_atomic = False


class Database(object):
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri, isolation_level="AUTOCOMMIT")
        self.Session = sessionmaker(bind=self.engine, class_=Session, autocommit=True)

        # Keep track of which DBAPI connection(s) had autocommit turned off for
        # a particular transaction object.
        dconns_by_trans = {}

        @event.listens_for(self.Session, 'after_begin')
        def receive_after_begin(session, transaction, connection):
            """When a (non-nested) transaction begins, turn autocommit off."""
            dbapi_connection = connection.connection.connection
            if transaction.nested:
                assert not dbapi_connection.autocommit
                return
            assert dbapi_connection.autocommit
            dbapi_connection.autocommit = False
            dconns_by_trans.setdefault(transaction, set()).add(
                dbapi_connection)

        @event.listens_for(self.Session, 'after_transaction_end')
        def receive_after_transaction_end(session, transaction):
            """Restore autocommit anywhere this transaction turned it off."""
            if transaction in dconns_by_trans:
                for dbapi_connection in dconns_by_trans[transaction]:
                    assert not dbapi_connection.autocommit
                    dbapi_connection.autocommit = True
                del dconns_by_trans[transaction]
