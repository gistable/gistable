from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
     Boolean, Unicode, Numeric as _Numeric, Date, Time, ForeignKey, Table, and_, \
     create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, relation, class_mapper
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta

import os
import sys
import csv
from itertools import chain, islice
from datetime import time, date, datetime

from pytz import UTC

Session = scoped_session(sessionmaker(expire_on_commit=False))

Numeric = _Numeric(10,4)

class BaseDeclarativeMeta(DeclarativeMeta):
    def __getattr__(self, name):
        if name.startswith("get_by_"):
            field = name[len("get_by_"):]
            return lambda value: self.get_by(
                self.__getattribute__(self, field),
                value
            )
        elif name.startswith('find_by_'):
            field = name[len("find_by_"):]
            return lambda value: self.find(
                self.__getattribute__(self, field) == value
            )
        else:
            return super(BaseDeclarativeMeta, self).__getattribute__(name)

class BaseModel(object):

    objects = Session.query_property()

    @property
    def columns(self):
        return [ i.key for i in class_mapper(self.__class__).iterate_properties
                 if isinstance(i, ColumnProperty) ]

    @property
    def relationships(self):
        return [ i.key for i in class_mapper(self.__class__).iterate_properties
                 if isinstance(i, RelationshipProperty) ]
    @property
    def primary_key(self):
        return [i.key for i in class_mapper(self.__class__).primary_key]

    @property
    def attributes(self):
        return self.columns + self.relationships

    def update(self, data):
        for attr in self.columns:
            if attr in data and data[attr] != getattr(self, attr):
                setattr(self, attr, data[attr])
        return self

    def to_dict(self, include=None, exclude=None):
        '''
        Returns a dict of attributes of a mapped instance
        '''

        cols = self.columns

        rv = {}
        for col in cols:

            if include and col not in include:
                continue

            if exclude and col in exclude:
                continue

            val = getattr(self, col)

            rv[col] = val
            
        return rv

    @classmethod
    def get(cls, id):
        return cls.objects.get(id)

    @classmethod
    def get_by(cls, column, value):
        try:
            return cls.objects.filter(column==value).one()
        except NoResultFound:
            return None

    @classmethod
    def find(cls, criteria):
        return cls.objects.filter(criteria)

    @classmethod
    def find_one(cls, criteria):
        try:
            return cls.find(criteria).one()
        except NoResultFound:
            return None
        
    @classmethod
    def __or_create__(cls, o, data, update):
        status = False

        if not o:
            o = cls(**data)
            Session.add(o)
            status = True
        elif update:
            o.update(data)

        return o, status
        
    @classmethod
    def get_or_create(cls, id, data, update=True):
        return cls.__or_create__(cls.get(id), data, update)

    @classmethod
    def get_by_or_create(cls, column, value, data, update=True):
        return cls.__or_create__(cls.get_by(column, value), data, update)

    @classmethod
    def find_or_create(cls, criteria, data, update=True):
        return cls.__or_create__(cls.find_one(criteria), data, update)

class UTCDateTime(TypeDecorator):
        impl = DateTime

        def convert_bind_param(self, value, engine):
            return value
        
        def convert_result_value(self, value, engine):
            return UTC.localize(value)

class GTFSBaseModel(BaseModel):

    @classmethod
    def from_csv(cls, data):
        return data

Base = declarative_base(cls=GTFSBaseModel, metaclass=BaseDeclarativeMeta)

class Agency(Base):
    __tablename__ = 'agency'

    agency_id = Column(Integer, primary_key=True)
    agency_name = Column(String, nullable=False)
    agency_url = Column(String, nullable=False)
    agency_timezone = Column(String, nullable=False)
    agency_lang = Column(String, nullable=True)
    agency_phone = Column(String, nullable=True)
    agency_fare_url = Column(String, nullable=True)

class CalendarDate(Base):
    __tablename__ = 'calendar_dates'

    service_id = Column(Integer, primary_key=True)
    date = Column(Date, primary_key=True)
    exception_type = Column(Integer, primary_key=True)

    @classmethod
    def from_csv(cls, data):
        parts = [data['date'][0:4], data['date'][4:6], data['date'][6:8]]
        year, month, day = (int(i) for i in parts)
        data['date'] = date(year, month, day)
        return data

    
class Stop(Base):
    __tablename__ = 'stops'

    stop_id = Column(Integer, primary_key=True)
    stop_code = Column(String, nullable=True, unique=True)
    stop_name = Column(String, nullable=False)
    stop_desc = Column(String, nullable=True)
    stop_lat = Column(Numeric, nullable=False)
    stop_lon = Column(Numeric, nullable=False)
    zone_id = Column(Integer, nullable=True)
    stop_url = Column(String, nullable=True)
    location_type = Column(Integer, nullable=True)
    parent_station = Column(Integer, nullable=True)
    stop_timezone = Column(String, nullable=True)

class Route(Base):
    __tablename__ = 'routes'
        
    route_id = Column(Integer, primary_key=True)
    agency_id = Column(Integer, ForeignKey('agency.agency_id'), nullable=True)
    route_short_name = Column(String, nullable=False)
    route_long_name = Column(String, nullable=False)
    route_desc = Column(String, nullable=True)
    route_type = Column(Integer, nullable=False)
    route_url = Column(String, nullable=True)
    route_color = Column(String, nullable=True)
    route_text_color = Column(String, nullable=True)

    agency = relation(Agency)
    trips = relation('Trip', lazy='dynamic')


class Trip(Base):
    __tablename__ = 'trips'

    trip_id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.route_id'), nullable=False)
    service_id = Column(Integer, ForeignKey('calendar_dates.service_id'),
                        nullable=False)
    trip_headsign = Column(String, nullable=True)
    trip_short_name = Column(String, nullable=True)
    direction_id = Column(Integer, nullable=True)
    block_id = Column(Integer, nullable=True)
    shape_id = Column(Integer, ForeignKey('shapes.shape_id'), nullable=True)

    route = relation(Route)
    service = relation(CalendarDate)
    stops = relation('StopTime', order_by=lambda: StopTime.stop_sequence)
    
class StopTime(Base):
    __tablename__ = 'stop_times'

    trip_id = Column(Integer, ForeignKey('trips.trip_id'), primary_key=True)
    arrival_time = Column(Time, nullable=False)
    departure_time = Column(Time, nullable=False)
    stop_id = Column(Integer, ForeignKey('stops.stop_id'), primary_key=True)
    stop_sequence = Column(Integer, primary_key=True)
    stop_headsign = Column(String, nullable=True)
    pickup_type = Column(Integer, nullable=True)
    drop_off_type = Column(Integer, nullable=True)
    shape_dist_traveled = Column(Integer, nullable=True)

    trip = relation(Trip)
    stop = relation(Stop)
    
    @classmethod
    def from_csv(cls, data):
        for i in ['arrival_time', 'departure_time']:
            hour, minute, second = (int(j) for j in data[i].split(':'))
            if hour >= 24:
                hour -= 24

            data[i] = time(hour, minute, second)

        return data

class Shape(Base):
    __tablename__ = 'shapes'

    _id = Column(Integer, primary_key=True)

    shape_id = Column(Integer, nullable=False)
    shape_pt_lat = Column(Numeric, nullable=False)
    shape_pt_lon = Column(Numeric, nullable=False)
    shape_pt_seq = Column(Integer, nullable=True)
    shape_dist_traveled = Column(Numeric, nullable=True)



def chunked(seq, chunksize):
    """Yields items from an iterator in chunks."""
    it = iter(seq)
    while True:
        yield chain([it.next()], islice(it, chunksize-1))

def import_into(cls, root):
    path = os.path.join(root, cls.__tablename__ + '.txt')

    if not os.path.isfile(path):
        return 

    print 'Importing %s into %s...' % (path, cls.__tablename__)

    cls.__table__.drop()
    cls.__table__.create()

    with open(path, 'rb') as f:
        reader = csv.DictReader(f, delimiter=',')
        for chunk in chunked(reader, 1000):
            Session.execute(cls.__table__.insert(),
                            [cls.from_csv(i) for i in chunk])

def import_data(root):
    for cls in [Agency, Stop, Route, Trip, CalendarDate, Shape, StopTime]:
        import_into(cls, root)
        Session.commit()

def init_db(dsn):
    engine = create_engine(dsn, echo=False)
    Session.configure(bind=engine)
    Base.metadata.bind = engine

def init_sqlite_db(path):
    init_db('sqlite:///' + path)

def main():    
    
    init_sqlite_db('njtransit-bus.db')

    #import_data('njtransit-bus')

    route = Route.get_by_route_short_name('87')
    trips = route.trips              \
                 .join(StopTime)     \
                 .filter(StopTime.arrival_time > datetime.now()) \
                 .order_by(StopTime.arrival_time.asc())

    for trip in trips:
        print trip.trip_headsign
        for stop in trip.stops:
            print '   -', stop.stop.stop_name, stop.arrival_time
        print
        print

    return 0

if __name__ == '__main__':
    rv = main()
    sys.exit(rv)
