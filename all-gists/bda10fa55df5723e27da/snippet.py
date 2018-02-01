# -*- coding: utf-8 -*-

"""From a Query.all(), turn this result to a pandas DataFrame

Table creation and example data come from the official SQLAlchemy ORM
tutorial at http://docs.sqlalchemy.org/en/latest/orm/tutorial.html

Just take a look at the 'query_to_dict' function and the last part of the __main__.
"""


from __future__ import print_function
from collections import defaultdict

from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import pandas as pd


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __repr__(self):
       return "<User(name='%s', fullname='%s', password='%s')>" % (
                            self.name, self.fullname, self.password)

def populate(session):
    ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
    session.add(ed_user)
    session.add_all([
        User(name='wendy', fullname='Wendy Williams', password='foobar'),
        User(name='mary', fullname='Mary Contrary', password='xxg527'),
        User(name='fred', fullname='Fred Flinstone', password='blah')])
    session.commit()

def query_to_list(rset):
    """List of result

    Return: columns name, list of result
    """
    result = []
    for obj in rset:
        instance = inspect(obj)
        items = instance.attrs.items()
        result.append([x.value for _,x in items])
    return instance.attrs.keys(), result

def query_to_dict(rset):
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)
    return result

if __name__ == '__main__':
    # Engine & session
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Put some data.
    populate(session)
    # Query
    rset = session.query(User).all()
    # Give me a DataFrame
    # Inconvenient: it's not well ordered (e.g. 'id' is not the first)
    df = pd.DataFrame(query_to_dict(rset))
    print(df)
    names, data = query_to_list(rset)
    df2 = pd.DataFrame.from_records(data, columns=names)
