#!/usr/bin/env python
#-*- coding:utf8 -*-

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Date
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.types import TypeDecorator
from sqlalchemy import DateTime as SdateTime
import time
import pytz

tz = pytz.timezone('America/Chicago')
class DateTime(TypeDecorator):
    impl = SdateTime
    def process_bind_param(self, value, engine):
        return value
    def process_result_value(self, value, engine):
        return value.replace(tzinfo=pytz.timezone('Asia/Tokyo')).astimezone(tz)

dsn = 'mysql://testuser:testpass@localhost/test'
engine = create_engine(dsn, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                 autoflush=False,
                                 bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    cdate = Column(Date, default=datetime.today().strftime("%Y-%m-%d"), nullable=False)
    datetime = Column(DateTime, default=datetime.now, nullable=False)

if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db_session.add(Entry())
    db_session.commit()

    e = db_session.query(Entry).first()
    print e.datetime

