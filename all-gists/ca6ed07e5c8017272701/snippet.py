"""
From http://harkablog.com/inside-the-django-orm-aggregates.html
with a couple of fixes.

Usage: MyModel.objects.all().annotate(new_attribute=Concat('related__attribute', separator=':')
"""

from django.db.models import Aggregate
from django.db.models.sql.aggregates import Aggregate as SQLAggregate


class Concat(Aggregate):
    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = SQLConcat(col, source=source, is_summary=is_summary, **self.extra)
        query.aggregates[alias] = aggregate


class SQLConcat(SQLAggregate):
    sql_function = 'group_concat'

    @property
    def sql_template(self):
        separator = self.extra.get('separator')
        if separator:
            return '%(function)s(%(field)s, "%(separator)s")'
        else:
            return '%(function)s(%(field)s)'
