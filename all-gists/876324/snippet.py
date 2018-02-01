from itertools import imap
from collections import namedtuple

from django.db.models.query import QuerySet, ValuesQuerySet


class NamedTuplesQuerySet(ValuesQuerySet):
    def iterator(self):
        # Purge any extra columns that haven't been explicitly asked for
        extra_names = self.query.extra_select.keys()
        field_names = self.field_names
        aggregate_names = self.query.aggregate_select.keys()

        names = extra_names + field_names + aggregate_names
        tuple_cls = namedtuple('%sTuple' % self.model.__name__, names)

        # NOTE: we are not reordering fields here,
        #       so they can go not in that order as in .namedtuples args
        #       if extra or aggregates are used.
        results_iter = self.query.get_compiler(self.db).results_iter()
        return imap(tuple_cls._make, results_iter)


def namedtuples(self, *fields):
    return self._clone(klass=NamedTuplesQuerySet, setup=True, _fields=fields)
QuerySet.namedtuples = namedtuples