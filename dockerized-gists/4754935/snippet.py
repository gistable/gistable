from sqlalchemy.orm.query import Query
from sqlalchemy.sql import ClauseElement
from sqlalchemy import cast, Boolean


class PublicQuery(Query):

    '''
    Filters all queries by publicity condition for each participating mapped
    class. Attribute "public" of mapped class (if present) should be either
    boolean column or @hybrid_property providing publicity criterion clause for
    the class and boolean (convertable to boolean) value for instance of the
    class.

    A bit modified version of recipe from
    http://www.sqlalchemy.org/trac/wiki/UsageRecipes/PreFilteredQuery
    '''

    def get(self, ident):
        obj = Query.get(self, ident)
        if obj is not None and getattr(obj, 'public', True):
            return obj
        # Other option:
        # override get() so that the flag is always checked in the 
        # DB as opposed to pulling from the identity map. - this is optional.
        #return Query.get(self.populate_existing(), ident)

    def __iter__(self):
        return Query.__iter__(self.private())

    def from_self(self, *ent):
        # override from_self() to automatically apply
        # the criterion too.   this works with count() and
        # others.
        return Query.from_self(self.private(), *ent)

    def private(self):
        mzero = self._mapper_zero()
        if mzero is not None and \
                getattr(mzero.class_, 'public', None) is not None:
            crit = mzero.class_.public
            if not isinstance(crit, ClauseElement):
                # This simplest safe way to make bare boolean column accepted
                # as expression.
                crit = cast(crit, Boolean)
            # XXX It's dangerous since it can mask errors
            return self.enable_assertions(False).filter(crit)
        else:
            return self


from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    public = Column(Boolean, nullable=False)
    addresses = relation("Address", backref="user")


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    public = Column(Boolean, nullable=False)


engine = create_engine('sqlite://')#, echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, query_cls=PublicQuery)
    
sess = Session()

sess.add_all([
    User(name='u1', public=True,
         addresses=[Address(email='u1a1', public=True),
                    Address(email='u1a2', public=True)]),
    User(name='u2', public=True,
         addresses=[Address(email='u2a1', public=False),
                    Address(email='u2a2', public=True)]),
    User(name='u3', public=False,
         addresses=[Address(email='u3a1', public=False),
                    Address(email='u3a2', public=False)]),
    User(name='u4', public=False,
         addresses=[Address(email='u4a1', public=False),
                    Address(email='u4a2', public=True)]),
    User(name='u5', public=True,
         addresses=[Address(email='u5a1', public=True),
                    Address(email='u5a2', public=False)])
])

sess.commit()

entries = []
for ad in sess.query(Address):
    assert ad.public
    user = ad.user
    if user:
        assert user.public
        entries.append((ad.email, user.name))
    else:
        entries.append((ad.email, None))

assert entries == [
    (u'u1a1', u'u1'),
    (u'u1a2', u'u1'),
    (u'u2a2', u'u2'),
    (u'u4a2', None),
    (u'u5a1', u'u5'),
]

a1 = sess.query(Address).filter_by(email='u1a1').one()
a1_user_id = a1.user.id
assert sess.query(User).get(a1_user_id) is not None
a1.user.public = False
sess.commit()

assert a1.user is None
assert sess.query(User).get(a1_user_id) is None

assert sess.query(User).order_by(User.name).first().name=='u2'

assert list(sess.query(User).values(User.name)) == [('u2',), ('u5',)]
assert sess.query(User.name).all() == [('u2',), ('u5',)]
assert sess.query(User).count()==2


# XXX The following assertions fail:

assert sess.query(User.name).join(User.addresses).filter(Address.email=='u2a1').all()==[]
assert sess.query(User.name).filter(User.addresses.any(email='u2a1')).all()==[]
assert sess.query(User.name, Address.email).join(Address.user).all()==[('u2', 'u2a2'), ('u5', 'u5a1')]
assert sess.query(Address.email, User.name).join(Address.user).all()==[('u2a2', 'u2'), ('u5a1', 'u5')]
