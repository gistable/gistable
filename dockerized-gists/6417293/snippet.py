#!/usr/bin/env python
import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.orm import validates
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    started_at = Column(DateTime)
    stopped_at = Column(DateTime)

    # Solution 1. Use a Check Constraint on your object
    __table_args__ = (
        CheckConstraint('started_at <= stopped_at'),
    )

    # Solution 2. Use a logical constraing
    # This constraint will check the value of the two datetime fields.
    # At the first call, the started_at field will be filled by the value of
    # field, but not the stopped_at field. This one will be None.

    # At the second call, the key will be for the 'stopped_at' field and the
    # value will contain the value of this field.

    # for this reason, I check the value of the 'key' parameter and I check if
    # the self.started_at field is an instance of 'datetime.datetime'.
    # Then, I can check the values of these two fields and raise an exception if
    # there is an error.
    @validates('started_at', 'stopped_at')
    def validate_dates(self, key, field):
        print "started, stopped: %r %r" %( self.started_at, self.stopped_at)
        print "key, field:  %r %r" % (key, field,)
        if key == 'stopped_at' and isinstance(self.started_at, datetime.datetime):
            if self.started_at > field:
                raise AssertionError("The stopped_at field must be "\
                                     "greater-or-equal than the started_at field")
        return field

engine = create_engine('sqlite:///:memory:', echo=True)

Base.metadata.create_all(engine)

event = Event(name='Event1',
              started_at=datetime.datetime.now(),
              stopped_at=datetime.datetime.now(),
              )

Session = sessionmaker(bind=engine)

try:
    session = Session()
    session.add(event)
    session.commit()
except IntegrityError as ex:
    print ex

