import itertools
from collections import Iterator

from lifter import utils


class Order(object):
    ASC = 1
    DECS = 2


class Path(object):
    def __init__(self, path=None):
        self.path = path or []

    def __getattr__(self, part):
        return self.__class__(self.path + [part])

    __getitem__ = __getattr__

    def __str__(self):
        return '.'.join(self.path)

    def get(self, data):
        for part in self.path:
            if part in data:
                data = data[part]
            else:
                raise ValueError('wrong path')

        return data


class Aggregation(Path):
    def __call__(self, aggregate):
        self.aggregate = aggregate

        return self

    def __repr__(self):
        return 'Aggregation({})'.format(self.aggregate)

    def aggregate(self, data):
        yield from self.aggregate(data)


class QueryImpl(object):
    def __init__(self, test, hashval):
        self.test = test
        self.hashval = hashval

    def __repr__(self):
        template = 'QueryImpl({0} {1})' if len(self.hashval) == 2 else 'QueryImpl({1} {0} {2})'

        return template.format(*self.hashval)

    def __call__(self, val):
        return self.test(val)

    def __and__(self, other):
        return QueryImpl(
            lambda val: self(val) and other(val),
            ('&', self, other)
        )

    def __or__(self, other):
        return QueryImpl(
            lambda val: self(val) or other(val),
            ('|', self, other)
        )

    def __invert__(self):
        return QueryImpl(
            lambda val: not self(val),
            ('not', self, '')
        )


class Query(Path):
    def _generate_test(self, test, hashval):
        def impl(value):
            return test(self.get(value))

        return QueryImpl(impl, hashval)

    def __call__(self, callable):
        raise NotImplementedError()

    def __eq__(self, other):
        return self._generate_test(
            lambda val: val == other, ('==', self, other)
        )

    def __ne__(self, other):
        return self._generate_test(
            lambda val: val != other, ('!=', self, other)
        )

    def __gt__(self, other):
        return self._generate_test(
            lambda val: val > other, ('>', self, other)
        )

    def __ge__(self, other):
        return self._generate_test(
            lambda val: val >= other, ('>=', self, other)
        )

    def __lt__(self, other):
        return self._generate_test(
            lambda val: val < other, ('<', self, other)
        )

    def __le__(self, other):
        return self._generate_test(
            lambda val: val <= other, ('<=', self, other)
        )

    def test(self, func):
        return self._generate_test(
            func, ('test', self, func)
        )

    # __contains__, matches, search, any, all, exists probably


class TinyQuerySet(object):
    def __init__(self, data):

        if isinstance(data, Iterator):
            self._iter_data = data
            self._data = []
        else:
            self._iter_data = None
            self._data = data

    @property
    def __data(self):  # pretty ugly
        if self._iter_data:
            for val in self._iter_data:
                self._data.append(val)

                yield val

        self._iter_data = None

    @property
    def data(self):
        return itertools.chain(self._data, self.__data)

    def __iter__(self):
        for value in self.data:
            yield value

    def _clone(self, new_values):
        return self.__class__(new_values)

    def all(self):
        return self._clone(self.data)

    def get(self, query):
        return next(filter(query, self.data), None)

    def first(self):
        return next(self.data, None)

    def last(self):
        data = list(self.data)

        return data and data[-1] or None

    def filter(self, query):
        return self._clone(filter(query, self.data))

    def exclude(self, query):
        return self._clone(filter(lambda val: not query(val), self.data))

    def count(self):
        return len(list(self.data))

    def order_by(self, path, order=Order.ASC):
        reverse = order == Order.DECS

        def create_generator():
            yield from sorted(self.data, key=path.get, reverse=reverse) # sorted is not lazy

        return self._clone(create_generator())

    def values(self, *args):
        return self._clone(  # I believe in this case we should return raw data not query_set
            map(
                lambda val: {str(path):path.get(val) for path in args},
                self.data
            )
        )

    def values_list(self, *args, flat=False):  # "*args, flat=False" is Python 3.5 specific, will use **kwargs in older versions
        if not args:
            raise ValueError('Empty values')

        getter = lambda val: tuple(path.get(val) for path in args)

        if flat and len(args) > 1:
            raise ValueError('You cannot set flat to True if you want to return multiple values')
        elif flat:
            getter = lambda val: args[0].get(val)

        return self._clone(  # I believe in this case we should return raw data not query_set
            map(getter, self.data)
        )

    def aggregate(self, *args, flat=False, **kwargs):  # "*args, flat=False" is Python 3.5 specific, will use **kwargs in older versions
        data = {}  # Isn't lazy

        kwargs.update((str(aggregation), aggregation) for aggregation in args)

        for key, aggregation in kwargs.items():
            values = (aggregation.get(val) for val in self.data)
            data[key] = aggregation.aggregate(values)

        if flat:
            return list(data.values())  # Isn't lazy

        return data

    def distinct(self):
        return self._clone(utils.unique_everseen(self.data))


q = Query()  # filter, exclude, get
p = Path()  # order_by, values, values_list
a = Aggregation()  # aggregate