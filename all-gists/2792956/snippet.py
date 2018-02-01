#-*- coding: utf-8 -*-
import contextlib

from django.db import connection


@contextlib.contextmanager
def acquire_table_lock(read, write):
    '''Acquire read & write locks on tables.

    Usage example:
    from polls.models import Poll, Choice
    with acquire_table_lock(read=[Poll], write=[Choice]):
        pass
    '''
    cursor = lock_table(read, write)
    try:
        yield cursor
    finally:
        unlock_table(cursor)


def lock_table(read, write):
    '''Acquire read & write locks on tables.'''
    # MySQL
    if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
        # Get the actual table names
        write_tables = [model._meta.db_table for model in write]
        read_tables = [model._meta.db_table for model in read]
        # Statements
        write_statement = ', '.join(['%s WRITE' % table for table in write_tables])
        read_statement = ', '.join(['%s READ' % table for table in read_tables])
        statement = 'LOCK TABLES %s' % ', '.join([write_statement, read_statement])
        # Acquire the lock
        cursor = connection.cursor()
        cursor.execute(statement)
        return cursor
    # Other databases: not supported
    else:
        raise Exception('This backend is not supported: %s' %
                        connection.settings_dict['ENGINE'])


def unlock_table(cursor):
    '''Release all acquired locks.'''
    # MySQL
    if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
        cursor.execute("UNLOCK TABLES")
    # Other databases: not supported
    else:
        raise Exception('This backend is not supported: %s' %
                        connection.settings_dict['ENGINE'])
