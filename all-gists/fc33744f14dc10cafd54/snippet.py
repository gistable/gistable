from django.db import connections
from django.db.models.query import QuerySet
from __future__ import print_function

class QuerySetExplainMixin:
    def explain(self, analyze=True):
        cursor = connections[self.db].cursor()
        print(self.query)
        print()
        sql, params = self.query.sql_with_params()
        cursor.execute('EXPLAIN %s %s' % ("ANALYZE" if analyze else "", sql), params)
        map(lambda x: print(x[0]), cursor.fetchall())
        return None

QuerySet.__bases__ += (QuerySetExplainMixin,)
