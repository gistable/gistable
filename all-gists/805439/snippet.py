# tutorial/__init__.py

from pyramid.config import Configurator

from tutorial.model.meta import init_model
from tutorial.request import TutorialRequest

def main(global_config, **settings):
    init_model(settings)

    config = Configurator(settings=settings,
                          request_factory=TutorialRequest)

    return config.make_wsgi_app()


# tutorial/request.py
from pyramid.request import Request
from pyramid.decorator import reify

class TutorialRequest(Request):

    @reify
    def db(self):
        maker = self.registry.settings['db.maker']
        return maker()


# tutorial/model/meta.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def init_model(settings):
    from sqlalchemy import engine_from_config
    from sqlalchemy.orm import sessionmaker
    from zope.sqlalchemy import ZopeTransactionExtension

    engine = engine_from_config(settings, 'sqlalchemy.')
    settings['db.engine'] = engine

    maker = sessionmaker(bind=engine, extension=ZopeTransactionExtension())
    settings['db.maker'] = maker


# tutorial/model/users.py
import logging
from datetime import datetime
from hashlib import sha256

from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relation, backref
from sqlalchemy.types import Integer, DateTime, String

from baseline.model.meta import Base

__all__ = ['User', 'Group']

log = logging.getLogger(__name__)

user_group_table = Table('user_group_link', Base.metadata,
    Column('user_id', Integer,
           ForeignKey('user.id', ondelete='cascade', onupdate='cascade'),
           nullable=False),
    Column('group_id', Integer,
           ForeignKey('group.id', ondelete='cascade', onupdate='cascade'),
           nullable=False),
    UniqueConstraint('user_id', 'group_id')
)

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)

    login = Column(String(32), unique=True, index=True, nullable=False)

    signup_date = Column(DateTime, default=datetime.utcnow)
    last_login_date = Column(DateTime, default=datetime.utcnow)

    groups = relation('Group', secondary=user_group_table,
                      backref='users')

    def __repr__(self):
        return '<User(id=%r, login=%r)>' % (self.id, self.login)

class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True, index=True)

    def __repr__(self):
        return '<Group(id=%r, name=%r)>' % (self.id, self.name)


# tutorial/model/__init__.py
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from users import *


## NOTES
#   The database connection is available through either ``request.db`` or
#   ``config.registry.settings['db.maker']``.
#
#   This method relies on the fact that SQLAlchemy uses the QueuePool
#   connection pool by default which is thread-safe (or the SingletonPool
#   for SQLite).