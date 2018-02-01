#!/usr/bin/env python
# -*- coding: utf-8 -*-

import code
import logging

from datetime import datetime

from sqlalchemy import create_engine, event
from sqlalchemy import Column, Float, Integer, MetaData, UnicodeText
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import geoalchemy
from geoalchemy.postgis import PGComparator

# Edit to reflect the db name, user and password to connect to your
# postgis database.
DB_SETTINGS = dict(
    db_name = '...', 
    db_user = '...', 
    db_password = '...', 
    db_host = 'localhost', 
    db_port = 5432
)

def engine_factory():
    """Creates the database engine."""
    
    settings = DB_SETTINGS
    postgresql_path = 'postgresql://%s:%s@%s:%s/%s' % (
        settings['db_user'],
        settings['db_password'],
        settings['db_host'],
        settings['db_port'],
        settings['db_name']
    )
    return create_engine(postgresql_path)

engine = engine_factory()

Session = scoped_session(sessionmaker(bind=engine))
SQLModel = declarative_base()

class Geography(geoalchemy.Geometry):
    """Subclass of `Geometry` that stores a `Geography Type`_.
      
      Defaults to storing a point.  Call with `specific=False` if you don't
      want to define the geography type it stores, or specify using
      `geography_type='POLYGON'`, etc.
      
      _`Geography Type`: http://postgis.refractions.net/docs/ch04.html#PostGIS_Geography
    """
    
    @property
    def name(self):
        if not self.kwargs.get('specific', True):
            return 'GEOGRAPHY'
        geography_type = self.kwargs.get('geography_type', 'POINT')
        srid = self.kwargs.get('srid', 4326)
        return 'GEOGRAPHY(%s,%d)' % (geography_type, srid)
        
    
    


class Message(SQLModel):
    """Encapsulate a geolocated message."""
    
    __tablename__ = 'message'
    
    query = Session.query_property()
    
    id =  Column(Integer, primary_key=True)
    content = Column(UnicodeText)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = geoalchemy.GeometryColumn(Geography(2), comparator=PGComparator)
    
    def update_location(self):
        """Update `self.location` with a point value derived from 
          `self.latitude` and `self.longitude`.  
          
          Note that the point will be `autocast`_ to geography type on saving:
          
          > Standard geometry type data will autocast to geography if it is of 
            SRID 4326.
          
          `autocast`: http://postgis.refractions.net/docs/ch04.html#Geography_Basics
        """
        
        self.location = "POINT(%0.8f %0.8f)" % (self.longitude, self.latitude)
        
    
    
    @classmethod
    def within_clause(cls, latitude, longitude, distance):
        """Return a within clause that explicitly casts the `latitude` and 
          `longitude` provided to geography type.
        """
        
        attr = '%s.location' % cls.__tablename__
        
        point = 'POINT(%0.8f %0.8f)' % (longitude, latitude)
        location = "ST_GeographyFromText(E'SRID=4326;%s')" % point
        
        return 'ST_DWithin(%s, %s, %d)' % (attr, location, distance)
        
    
    
    def __repr__(self):
        return self.content
        
    
    


# Bind `Message` before insert or update events to `msg.update_location()`.
handler = lambda mapper, connection, target: target.update_location()
for event_name in 'before_insert', 'before_update':
    event.listen(Message, event_name, handler)
    

SQLModel.metadata.create_all(engine)

points = (
    (51.5192028, -0.140863, u'great titchfield street'),
    (51.5255764, -0.0881744, u'old street'),
    (51.5457865, -0.0554184, u'hackney'),
    (51.889378, 0.261515, u'stanstead airport'),
    (-37.8167, 144.9667, u'melbourne australia')
)

def within(distance):
    """Get all messages within `distance` from `points[0]`."""
    
    lat = points[0][0]
    lng = points[0][1]
    
    clause = Message.within_clause(lat, lng, distance)
    query = Message.query.filter(clause)
    
    return query.all()
    


def reset():
    """Reset the database."""
    
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    

def populate():
    """Populate the database."""
    
    session = Session()
    for data in points:
        message = Message(
            latitude=data[0],
            longitude=data[1],
            content=data[2]
        )
        session.add(message)
    try:
        session.commit()
    except IntegrityError, err:
        logging.error(err)
        session.rollback()
    finally:
        session.close()
    


def test():
    """Test that the geography type within distance queries are correct."""
    
    assert str(within(1)[-1]) == 'great titchfield street'
    assert str(within(10 * 1000)[-1]) == 'hackney'
    assert 'melbourne australia' != str(within(16800 * 1000)[-1])
    assert 'melbourne australia' == str(within(16900 * 1000)[-1])
    


if __name__ == '__main__':
    reset()
    populate()
    test()
    code.interact(local=locals())
    

