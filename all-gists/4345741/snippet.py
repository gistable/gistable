import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker

DBSession = scoped_session(sessionmaker())
class BaseMixin(object):
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

Base = declarative_base(cls=BaseMixin)


class Person(Base):
    name = sa.Column(sa.String(255))
    age = sa.Column(sa.Integer)
    gender = sa.Column(sa.types.Enum("boy","girl"))

engine = sa.create_engine("sqlite://")
engine.echo = True
Base.metadata.bind = engine
Base.metadata.create_all()
DBSession.configure(bind=engine)

class Rows(object):
    def __init__(self, header, rows):
        self.header = header
        self.rows = rows

    def commit(self, model, session=DBSession, commiter=DBSession):
        header = self.header
        for row in self.rows:
            o = model(**dict(zip(header,row)))
            session.add(o)
        commiter.commit()

rows = Rows(
    ["name","age","gender"],
    [("foo",10,"boy"),
     ("fooo",11,"boy"),
     ("foooo",12,"boy"),
     ("fooooo",13,"boy"),
     ("bar",10,"girl"),
     ("barr",11,"girl"),
     ("barrr",12,"girl"),
     ])
rows.commit(Person)

## using case
print Person.query.count()
print Person.query.filter_by(gender="girl").count()
print Person.query.filter_by(gender="boy").count()
print DBSession().query(sa.func.sum(sa.case([(Person.gender=="girl", 1)], else_=0)),
                        sa.func.sum(sa.case([(Person.gender=="boy", 1)], else_=0)),
                        sa.func.max(Person.age)).all()

## using case with with_entities
print Person.query.filter(Person.name.like("%ooo"))\
    .with_entities(sa.func.sum(sa.case([(Person.gender=="boy",1)],else_=0)))\
    .all()


## add column
print DBSession().query(Person.name).first()
print DBSession().query(Person.name).add_column(Person.age).first()


### aliased (self join)
p0, p1  = orm.aliased(Person,name="p0"), orm.aliased(Person ,name="p1")
import pprint

## permtation
pprint.pprint(
    DBSession.query(p0, p1)\
        .filter(p0.name!=p1.name)\
        .with_entities(p0.name,p1.name,p0.age,p1.age).all()
    )

## combination
pprint.pprint(
    DBSession.query(p0,p1)\
        .filter(p0.name < p1.name)
        .with_entities(p0.name,p1.name,p0.age,p1.age).all()
    )


### 
class Fruit(Base):
    name = sa.Column(sa.String(255))

Base.metadata.create_all()

### remove duplicated elements
rows = Rows(["name"],
            [[x] for x in ["apple","apple", "apple", "banana", "orange"]])
rows.commit(Fruit)

assert Fruit.query.count() == 5

## using correlated subquery
f0 = orm.aliased(Fruit)
subq = Fruit.query.with_entities(sa.func.max(Fruit.id)).correlate(f0).filter(f0.name==Fruit.name)
print DBSession.query(f0).filter(f0.id == subq).with_entities(f0.name).all()

## using group by
print Fruit.query.group_by(Fruit.name).with_entities(Fruit.name).all()


