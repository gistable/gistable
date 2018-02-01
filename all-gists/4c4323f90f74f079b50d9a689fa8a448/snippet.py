
from collections.abc import Iterator

class Maybe(Iterator):
    """ Iterator takes the place of Functor """
    __map_index__ = 0

    def __init__(self):
        super(self).__init__(self)

    def is_just(self):
        return self.value != None

    def unsafe_get(self):
        return self.value

    def __iter__(self):
        return self

    def __next__(self):
        self.__map_index__ += 1
        if self.value == None or self.__map_index__ > 1:
            self.__map_index__ = 0
            raise StopIteration
        else:
            return self.value

    @staticmethod
    def bind(computation):
        try:
          x = computation()
          return Just(x)
        except:
          return Nothing()

class Just(Maybe):
    def __init__(self, x):
        assert x != None
        self.value = list(x)[0] if isinstance(x, Iterator) else x

    def from_just(self):
        return self.value

    def __eq__(self, other):
        return isinstance(other, Just) and other.value == self.value

    def __repr__(self):
        return "Just(" + str(self.value) + ")"

class Nothing(Maybe):
    def __init__(self):
        self.value = None

    def __eq__(self, other):
        return isinstance(other, Nothing)

    def __repr__(self):
        return "Nothing"


""" definitely fragile helpers """

def filter_just(xs):
    if isinstance(xs, list):
        f = filter(lambda x: x.is_just(), xs)
        return list(map(lambda x: x.from_just(), f))
    if isinstance(xs, map):
        f = list(filter(lambda x: x.is_just(), list(xs)))
        return list(map(lambda x: x.from_just(), f))
    else:
        return []

def as_nonempty_list(xs):
    tmp = xs
    if not isinstance(xs, list):
        tmp = list(xs)
    return Nothing() if len(tmp) == 0 else Just(tmp)

def filter_nonempty_justs(xs):
    return as_nonempty_list(filter_just(xs))

def map_maybe(fn, maybe):
    """
    You can also do:
        Just(map(lambda x: x+3, Just(4)))
    which is equal to:
        map_maybe(lambda x: x+3, Just(4))
    but the latter will catch any errors:
        def error(): raise Exception()
        print(map_maybe(error, Just(4))) # Nothing
    """
    return Maybe.bind(lambda: fn(maybe.from_just())) if maybe.is_just() else Nothing()