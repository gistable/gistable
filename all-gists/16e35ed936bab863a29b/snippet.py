from maybe import Maybe
from validation import Validation


def Typeclass():
    class _Typeclass(object):
        registered_class = {}

        @classmethod
        def instance_for(cls, object_type):
            def wrapper(instance_cls):
                cls.registered_class[object_type] = instance_cls()
                return instance_cls

            return wrapper

        @classmethod
        def get_instance_for(cls, obj):
            def findFor(object_type):
                for instance_cls in cls.registered_class.keys():
                    if issubclass(object_type, instance_cls):
                        return instance_cls
                return None

            return cls.registered_class[findFor(obj.__class__)]

    return _Typeclass


# ----

class Functor(Typeclass()):
    def map(self, callable, functor):
        pass


@Functor.instance_for(Maybe)
class MaybeFunctor(Functor):
    def map(self, callable, functor):
        return functor.map(callable)


@Functor.instance_for(Validation)
class ValidationFunctor(Functor):
    def map(self, callable, functor):
        return functor.map(callable)


def map(callable, functor):
    return Functor.get_instance_for(functor).map(callable, functor)


# ----

class Monad(Typeclass()):
    def flatmap(self, callable, monad):
        pass

@Monad.instance_for(Maybe)
class MaybeMonad(Monad):
    def flatmap(self, callable, monad):
        return monad.flatmap(callable)

@Monad.instance_for(Validation)
class ValidationMonad(Monad):
    def flatmap(self, callable, monad):
        return monad.flatmap(callable)

def flatmap(callable, monad):
    return Monad.get_instance_for(monad).flatmap(callable, monad)

# ----

if __name__ == '__main__':
    from maybe import Just
    from validation import Success

    print(map(lambda x: x + 5, Just(10)))
    print(map(lambda x: x + 5, Success(10)))

    print(flatmap(lambda x: Just(x + 5), Just(10)))
    print(flatmap(lambda x: Success(x + 5), Success(10)))
