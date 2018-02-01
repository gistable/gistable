"""
A demo of creating a new database via SQL Alchemy.

Under MIT License from sprin (https://gist.github.com/sprin/5846464/)

This module takes the form of a nosetest with three steps:
    - Set up the new database.
    - Create a table in the new database.
    - Teardown the new database.
"""
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
)
from sqlalchemy.pool import NullPool

# XXX: It is advised to use another user that can connect to a default database,
# and has CREATE DATABASE permissions, rather than use a superuser.
DB_CONFIG_DICT = {
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': 5432,
}

DB_CONN_FORMAT = "postgresql://{user}:{password}@{host}:{port}/{database}"

DB_CONN_URI_DEFAULT = (DB_CONN_FORMAT.format(
    database='postgres',
    **DB_CONFIG_DICT))

engine_default = create_engine(DB_CONN_URI_DEFAULT)

NEW_DB_NAME = 'test'

DB_CONN_URI_NEW = (DB_CONN_FORMAT.format(
    database=NEW_DB_NAME,
    **DB_CONFIG_DICT))

metadata = MetaData()

proj = Table('test', metadata, Column('id', Integer))

def setup_module():
    conn = engine_default.connect()
    conn.execute("COMMIT")
    # Do not substitute user-supplied database names here.
    conn.execute("CREATE DATABASE %s" % NEW_DB_NAME)
    conn.close()

def test_create_table():
    # Get a new engine for the just-created database and create a table.
    engine_new = create_engine(DB_CONN_URI_NEW, poolclass=NullPool)
    conn = engine_new.connect()
    metadata.create_all(conn)
    conn.close()

def teardown_module():
    conn = engine_default.connect()
    conn.execute("COMMIT")
    # Do not substitute user-supplied database names here.
    conn.execute("DROP DATABASE %s" % NEW_DB_NAME)
    conn.close()
