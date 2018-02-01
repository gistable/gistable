#!/usr/bin/env python

import getopt
import sys
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.mysql.base import TINYINT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import ProgrammingError

def get_table_list_from_db(metadata):
    """
    return a list of table names from the current
    databases public schema
    """
    sql="select table_name from information_schema.tables where table_schema='public'"
    return [name for (name, ) in metadata.execute(sql)]

def make_session(connection_string):
    engine = create_engine(connection_string, echo=False, convert_unicode=True)
    Session = sessionmaker(bind=engine)
    return Session(), engine

def pull_data(from_db, to_db):
    print locals()
    source, sengine = make_session(from_db)
    smeta = MetaData(bind=sengine)
    destination, dengine = make_session(to_db)
    dmeta = MetaData(bind=dengine)

    dest_tables = get_table_list_from_db(dengine)

    for table_name in dest_tables:
        print 'Processing', table_name
        print 'Pulling schema from source server'
        table = Table(table_name, smeta, autoload=True)
        print 'Creating table on destination server'
        table.metadata.create_all(dengine)
        NewRecord = quick_mapper(table)
        columns = table.columns.keys()
        dest_table = Table(table_name, dmeta, autoload=True)
        dest_columns = dest_table.columns.keys()
        print 'Transferring records'
        for record in source.query(table).all():
            data = {}
            for column in dest_columns:
                value = getattr(record, column)
                if isinstance(table.columns[column].type, TINYINT):
                   value = bool(value)
                data[str(column)] = value

            destination.merge(NewRecord(**data))

    print 'Committing changes'
    destination.commit()

    print 'Fixing sequences'
    for table_name in dest_tables:
        table = Table(table_name, dmeta, autoload=True)
        columns = table.primary_key.columns.keys()
        print 'Fixing sequence for %s with primary key: %s' % (table_name, ' '.join(columns))
        try:
           dengine.execute("select setval('%(table_name)s_id_seq', max(%(primary_key)s)) from %(table_name)s" % {'table_name': table_name, 'primary_key': columns[0]})
        except ProgrammingError, e:
           print e

def print_usage():
    print """
Usage: %s -f source_server -t destination_server
    -f, -t = driver://user[:password]@host[:port]/database

Example: %s -f oracle://someuser:PaSsWd@db1/TSH1 \\
    -t mysql://root@db2:3307/reporting
    """ % (sys.argv[0], sys.argv[0])

def quick_mapper(table):
    Base = declarative_base()
    class GenericMapper(Base):
        __table__ = table
    return GenericMapper

if __name__ == '__main__':
    optlist, tables = getopt.getopt(sys.argv[1:], 'f:t:')

    options = dict(optlist)
    if '-f' not in options or '-t' not in options:
        print_usage()
        raise SystemExit, 1

    pull_data(
        options['-f'],
        options['-t'],
    )
