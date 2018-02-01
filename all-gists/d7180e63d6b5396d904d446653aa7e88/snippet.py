"""
Tornado/Momoko/AutoReload
=========================

Problem:
--------
If the connection to the database Postgres distructed - momoko can not re-create the connection pool.
To solve this problem you need to restart the application. To automate this process, I wrote a small script that use the built-in tornado update mechanism.

Solution:
---------
# Test every 1 second that database connection is alive.
# Add this check before you start ioloop.

import reload
check_connect = tornado.ioloop.PeriodicCallback(lambda: reload.reload_if_db_pool_is_dead(application.db), 1000)
check_connect.start()

License
-------
This code is distributed under the MIT license http://www.opensource.org/licenses/mit-license.php

"""
import momoko
import psycopg2
import tornado.autoreload
import tornado.gen
import tornado.web


@tornado.gen.coroutine
def reload_if_db_pool_is_dead(db):
    """
        Restart application if database connection is dead.
        It help to solve psycopg2 bug. To date, It's the most adequate and reliable solution.
    """
    try:
        cursor = yield db.execute('SELECT 1')
        cursor.fetchall()
    except (psycopg2.OperationalError, psycopg2.ProgrammingError, momoko.connection.Pool.DatabaseNotAvailable):
        tornado.autoreload._reload()
