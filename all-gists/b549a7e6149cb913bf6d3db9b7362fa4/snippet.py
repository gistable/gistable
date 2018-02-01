# -*- coding: utf-8 -*-


class Button:
    def __init__(self, foo, bar, text="Empty"):
        print id(self)
        print foo
        print bar
        print text


# Não valida
class Foo:
    def __init__(self):

        foo = 1
        bar = 2
        baz = 3

        self.buttons = Button(foo, bar,
                        text="JOGAR 1")


# Valida
class Baz:
    def __init__(self):

        foo = 4
        bar = 5
        baz = 6

        self.buttons = [Button(foo, bar,
                        text="JOGAR 2")]


Foo()
Baz()
