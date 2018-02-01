#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from basiclogger import pyLogger
#from datetime import datetime
from pandas import DataFrame
from sqlalchemy import create_engine

FILENAME = 'dataframetopostgres.log'


class Df2Pg:
    """Puts the data in the DataFrame in a Postgres database
    """
    class ReadFaker:
        """ This could be extended to include the index column optionally. Right now the index
        is not inserted
        """
        def __init__(self, data):
            self.iter = list(data.itertuples())

        def readline(self, size=None):
            try:
                prop = self.iter.pop(0)
                line = prop[1:]  # element 0 is the index
                row = '\t'.join(x if isinstance(x, str) else str(x) for x in line) + '\n'
            # in my case all strings in line are unicode objects.
            except IndexError:
                return ''
            else:
                return row

        read = readline

    def __init__(self, df, user, password, host, port, databasename, table, columns=None, logname=FILENAME):
        """ Gets:

        df       - the dataframe
        table    - the table name
        conn_str - psycopg2 connection string
        columns  - list with field names

        example:

          Df2Pg(df, user, pass, host, port, dbname, 's_schema.t_table', ['field1','field2'])

        """
        self.logger = pyLogger(logname, 'INFO')

        conn_str = 'postgres://{}:{}@{}:{}/{}'.format(user, password, host, port, databasename)

        self.__insert(df, table, conn_str, columns)

    def __insert(self, df, table, conn_str, columns=None):

        #time1 = datetime.now()
        close_con = False

        inserted_rows = df.shape[0]
        data = self.ReadFaker(df)
        con = psycopg2.connect(conn_str)

        try:
            curs = con.cursor()
            # self.logger.log.debug('inserting %s entries into %s ...' % (inserted_rows, table))
            if columns is not None:
                curs.copy_from(data, table, null='nan', columns=[col for col in columns])
            else:
                curs.copy_from(data, table, null='nan')
            con.commit()
            curs.close()
            if close_con:
                con.close()
        except psycopg2.Error as e:
            self.logger.log.error(e.pgerror)
            self.logger.log.error(e.pgcode)
            con.rollback()
            if close_con:
                con.close()
            raise e

        #time2 = datetime.now()
        # self.logger.log.debug(time2 - time1)
        self.logger.close()
        return inserted_rows


class Pg2Df():
    """Converts a pg database query into a Pandas DataFrame"""
    def __init__(self, user, password, host, port, databasename, sql, logname=FILENAME):

        self.logger = pyLogger(logname, 'INFO')
        self.__insert(user, password, host, port, databasename, sql)

    def __insert(self, user, password, host, port, databasename, sql):
        """Creates the engine, sends the SQL retrieves the DataFrame"""
        try:
            connstring = 'postgres://{}:{}@{}:{}/{}'.format(user, password, host, port, databasename)
            engine = create_engine(connstring, echo=False, implicit_returning=False)
            rs = engine.execute(sql)
            d = rs.fetchall()
            h = list(rs.keys())
            self.dtf = DataFrame.from_records(d, columns=h)
            engine.dispose()
        except Exception as e:
            self.logger.log.error('Error recuperando de la base de datos')
            self.logger.log.error(e)
            raise e
        self.logger.close()
        return self.dtf
