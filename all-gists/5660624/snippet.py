from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.compat import text_type

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import joinedload
import sqlalchemy as sa

from caching_query import FromCache
from caching_query import RelationshipCache
from caching_query import query_callable

from dogpile.cache import make_region

import hashlib
cache_region = make_region()

regions = {
    "default": cache_region
}

DBSession = scoped_session(
    sessionmaker(query_cls=query_callable(regions))
)


def md5_key_mangler(key):
    """Receive cache keys as long concatenated strings;
    distill them into an md5 hash.

    """
    d = hashlib.md5(key.encode('utf-8'))
    return d.hexdigest()


class BaseModel(object):
    @declared_attr
    def pk(self):
        return sa.Column(sa.Integer, primary_key=True)

    @declared_attr
    def date_created(self):
        return sa.Column(sa.DateTime)

Base = declarative_base(cls=BaseModel)

class User(Base):
    __tablename__ = 'users'
    username = sa.Column(sa.String)

class UserProfile(Base):
    __tablename__ = 'user_profile'
    first_name = sa.Column(sa.Unicode(255))
    user_pk = sa.Column(sa.Integer, sa.ForeignKey(User.pk))
    user = relationship(User, backref=backref('profile', uselist=False))

def get_user_by_username(session, username, with_profile=True,
        from_cache=True):

    query = session.query(User).filter(
        User.username == username
    )

    if with_profile:
        query = query.options(joinedload('profile'))

    if from_cache: 
        print("Pulling from cache")
        query = query.options(FromCache())
        query = query.options(RelationshipCache(User.profile))

    user = query.one()

    return user

def hello_world(request):
    user = get_user_by_username(DBSession, 'sontek')
    return Response('hello! user #%d' % user.pk)

def main():
    config = Configurator()

    engine = create_engine('sqlite:///foo.db')

    DBSession.configure(bind=engine)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    user1 = User(
        username=text_type('sontek')
    )

    profile = UserProfile(
        user=user1
        , first_name=text_type('John')
    )

    DBSession.add_all([user1, profile])

    cache_settings = {
        "cache.redis.backend":"dogpile.cache.redis",
        "cache.redis.arguments.host": "localhost",
        "cache.redis.arguments.port": 6379,
    }

    cache_region.configure_from_config(cache_settings, "cache.redis.")


    config.add_view(hello_world)
    app = config.make_wsgi_app()

    return app

if __name__ == '__main__':
    app = main()
    server = make_server('0.0.0.0', 8080, app)
    print("Serving at: http://0.0.0.0:8080")
    server.serve_forever()
