class Monad:
    @staticmethod
    def unit(val):
        raise NotImplemented

    def bind(self, fn):
        raise NotImplemented

    def map(self, map_fn):
        """
        map the result of this monad
        """
        return self.bind(lambda res: self.unit(map_fn(res)))

    def then(self, other):
        """
        sequence two monads
        """
        return self.bind(lambda _: other)

    def result(self, val):
        """
        replace the result and use only the side-effect
        """
        return self.bind(lambda _: self.unit(val))

    def skip(self, other):
        """
        sequence two monads, but preserve this result
        """
        return self.bind(lambda res: other.result(res))

    # >>
    def __rshift__(self, other):
        return self.then(other)

    # <<
    def __lshift__(self, other):
        return self.skip(other)

    @staticmethod
    def generate(iterfn):
        """
        combinator syntax (like haskell's `do`):

        @MyMonad.generate
        def a_monad():
            # like haskell's <-
            result = yield some_monad
            # return a monad instance here
            return MyMonad.unit(do_something_with(result))
        """
        def genmonad():
            iterator = iterfn()

            def send(val):
                try:
                    return iterator.send(val).bind(send)
                except StopIteration as result:
                    return result.value

            return send(None)

        return genmonad


class Maybe(Monad):
    @staticmethod
    def unit(val):
        return Just(val)

    class Just(Maybe):
        def __init__(self, val):
            self.value = val

        def bind(self, fn):
            return fn(self.value)

    class _Nothing(Maybe):
        def bind(self, fn):
            return self

    Nothing = _Nothing()
