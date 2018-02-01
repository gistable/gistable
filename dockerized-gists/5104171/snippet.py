"""SQLAlchemy Metadata and Session object"""
import datetime
import json
import time

from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker


__all__ = ['Session', 'metadata', 'Model', 'SchemaEncoder']


# Remove expire_on_commit=False if autorefreshing of committed objects is
# desireable.
Session = scoped_session(sessionmaker(expire_on_commit=False))
metadata = MetaData()


# Declarative base

from sqlalchemy.ext.declarative import declarative_base

class _Base(object):
    """ Metaclass for the Model base class."""
    # Only include these attributes when serializing using __json__. If
    # relationships should be serialized, then they need to be whitelisted.
    __json_whitelist__ = None

    @classmethod
    def get(cls, id):
        return Session.query(cls).get(id)

    @classmethod
    def get_by(cls, **kw):
        return Session.query(cls).filter_by(**kw).first()

    @classmethod
    def get_or_create(cls, **kw):
        r = cls.get_by(**kw)
        if r:
            return r

        return cls.create(**kw)

    @classmethod
    def create(cls, **kw):
        r = cls(**kw)
        Session.add(r)
        return r

    @classmethod
    def insert(cls, **kw):
        Session.execute(cls.__table__.insert(values=kw)).close()

    @classmethod
    def insert_many(cls, iter):
        Session.execute(cls.__table__.insert(), list(iter)).close()

    @classmethod
    def all(cls):
        return Session.query(cls).all()

    @classmethod
    def count(cls):
        return Session.query(cls).count()

    def delete(self):
        Session.delete(self)

    def refresh(self):
        Session.refresh(self)

    def __repr__(self):
        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys())
        return "%s(%s)" % (self.__class__.__name__, values)

    def __json__(self):
        if self.__json_whitelist__ is not None:
            return dict((k, getattr(self, k)) for k in self.__json_whitelist__)

        return dict((k, getattr(self, k)) for k in self.__table__.c.keys())


Model = declarative_base(metadata=metadata, cls=_Base)


class SchemaEncoder(json.JSONEncoder):
    """Encoder for converting Model objects into JSON."""

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return time.strftime('%Y-%m-%dT%H:%M:%SZ', obj.utctimetuple())
        elif isinstance(obj, Model):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)