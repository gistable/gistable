def curry(f, *args, **kwargs):
    def curried(*more_args, **more_kwargs):
        return f(*(args+more_args), **dict(kwargs, **more_kwargs))
    return curried


class Person(object):
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender

# Lightweight subclasses
Man = curry(Person, gender="Male")
Woman = curry(Person, gender="Female")

husband = Man("Donald")
wife = Woman("Donalina")

print husband.name, wife.name