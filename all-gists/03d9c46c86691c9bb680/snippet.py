import uuid
import psycopg2
from psycopg2.extras import DictCursor

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class LargeQueryConnectionMixin(object):
    """Going native on the db for speed and server side cursors
    which is necessary when dealing with very large result sets"""
    @classmethod
    def fetch(cls, sql, params_list):
        with psycopg2.connect(cls.db_dsn, cursor_factory=DictCursor) as conn:
            with conn.cursor() as c:
                c.execute("SET TIME ZONE %s", [settings.TIME_ZONE])
            # you must have psycopg2 >= 2.6 to get proper exec handling for cursor context manager
            # see https://github.com/psycopg/psycopg2/issues/262
            with conn.cursor(cls.ss_cursor_name) as c:
                c.itersize = 100  # 100 to 1000 should be reasonable
                c.execute(sql, params_list)
                for row in c:
                    yield row

    @classproperty
    def db_dsn(cls):
        return "dbname=%s user=%s" % (
            settings.DATABASES['default']['NAME'],
            settings.DATABASES['default']['USER'])

    @classproperty
    def ss_cursor_name(cls):
        "generates `random`ish server side cursor name"
        return 'cur_%s' % str(uuid.uuid4()).replace('-', '')[:10]


class Report(models.Model, LargeQueryConnectionMixin):
    created = models.DateTimeField()
    user = models.ForeignKey(User)
    # .... more model attribs

    @classmethod
    def some_specific_report(cls, limit=2000000):
        sql = "SELECT * from gigantic_table limit %s"
        return cls.fetch(sql, [limit])


# ------------ usage --------------
# this can churn through insanely huge result sets
# and memory usage will remain extremely low 
for row in Report.some_specific_report(100000):
    # write to disk and flush
    # with this generator 
    # data is accessed via row[INDEX] or row['COLUMN_NAME']
    print row



""" ____ PostgreSQL log verification ____
2015-04-22 12:24:08 EDT LOG:  statement: BEGIN
2015-04-22 12:24:08 EDT LOG:  statement: SET TIME ZONE 'US/Pacific'
2015-04-22 12:24:08 EDT LOG:  statement: DECLARE "cur_fa30e88f84" CURSOR WITHOUT HOLD FOR SELECT * from gigantic_table limit 100000
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: FETCH FORWARD 100 FROM "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: CLOSE "cur_fa30e88f84"
2015-04-22 12:24:08 EDT LOG:  statement: COMMIT
"""