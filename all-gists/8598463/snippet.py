# -*- coding: utf-8 -*-

class MagicDict(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
        self.__dict__ = self

    def __getattr__(self, name):
        self[name] = MagicDict()
        return self[name]


if __name__ == "__main__":
    c = MagicDict()

    c.people.name = 'roy'

    c.test1.test2.test3 = "test3"

    print(c)
    print(c.people)
    print(c.people.name)
    