import functools
import sys
import re
from django.conf import settings
from django.db import connection

def shrink_select(sql):
    return re.sub("^SELECT(.+)FROM", "SELECT .. FROM", sql)

def shrink_update(sql):
    return re.sub("SET(.+)WHERE", "SET .. WHERE", sql)

def shrink_insert(sql):
    return re.sub("\((.+)\)", "(..)", sql)

def shrink_sql(sql):
    return shrink_update(shrink_insert(shrink_select(sql)))

def _err_msg(num, expected_num, verbose, func=None):
    func_name = "%s:" % func.__name__ if func else ""
    msg = "%s Expected number of queries is %d, actual number is %d.\n" % (func_name, expected_num, num,)
    if verbose > 0:
        queries = [query['sql'] for query in connection.queries[-num:]]
        if verbose == 1:
            queries = [shrink_sql(sql) for sql in queries]
        msg += "== Queries == \n" +"\n".join(queries)
    return msg


def assertNumQueries(expected_num, verbose=1):

    class DecoratorOrContextManager(object):
        def __call__(self, func):  # decorator
            @functools.wraps(func)
            def inner(*args, **kwargs):
                handled = False
                try:
                    self.__enter__()
                    return func(*args, **kwargs)
                except:
                    self.__exit__(*sys.exc_info())
                    handled = True
                    raise
                finally:
                    if not handled:
                        self.__exit__(None, None, None)
            return inner

        def __enter__(self):
            self.old_debug = settings.DEBUG
            self.old_query_count = len(connection.queries)
            settings.DEBUG = True

        def __exit__(self, type, value, traceback):
            if not type:
                num = len(connection.queries) - self.old_query_count
                assert expected_num == num, _err_msg(num, expected_num, verbose)
            settings.DEBUG = self.old_debug

    return DecoratorOrContextManager()


# usage

    class MyTestCase(TestCase):
         
        @assertNumQueries(5)   
        def test_1(self):
           # ...

        def test_2(self):
           # ...
           with assertNumQueries(3, verbose=2): 
              # ...
           # ...