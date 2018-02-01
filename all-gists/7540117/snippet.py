from pyramid.security import ALL_PERMISSIONS
from pyramid.security import DENY_ALL
from pyramid.security import Allow
from pyramid.security import Everyone
from sqlalchemy import Column, Integer, Text, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, synonym
from zope.sqlalchemy import ZopeTransactionExtension

import cryptacular.bcrypt

ADMINS = []

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()
def hash_password(password):
    return unicode(crypt.encode(password))


def groupfinder(userid, request):
    """callback for authentication policy"""
    if userid in ADMINS:
        return ['g:admins']
    else:
        return []


class UserFactory(object):

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        user = User.get_by_username(key)
        user.__parent__ = self
        user.__name__ = key
        return user


class User(Base):

    @property
    def __acl__(self):
        return [
            (Allow, self.email, 'edit'),
            (Allow, 'g:admins', ALL_PERMISSIONS),
            (Allow, Everyone, 'view'), #DENY_ALL if no public user view
        ]

    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(Unicode(20), unique=True)
    name = Column(Unicode(50))
    email = Column(Unicode(50))
    hits = Column(Integer, default=0)
    misses = Column(Integer, default=0)
    delivered_hits = Column(Integer, default=0)
    delivered_misses = Column(Integer, default=0)
    _password = Column('password', Unicode(60))

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    def __init__(self, username, password, name, email):
        self.username = username
        self.name = name
        self.email = email
        self.password = password

    @classmethod
    def get_by_username(cls, username):
        return DBSession.query(cls).filter(cls.username == username).first()

    @classmethod
    def check_password(cls, username, password):
        user = cls.get_by_username(username)
        if not user:
            return False
        return crypt.check(user.password, password)