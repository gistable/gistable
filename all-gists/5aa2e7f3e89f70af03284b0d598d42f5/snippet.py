def check(cls):
    x1 = cls()
    x2 = cls()
    print(cls.__name__, id(x1.a), id(x2.a), id(cls.a), id(x1.a) == id(x2.a) == id(cls.a))


class X:
    a = {}


class Y:
    a = {}

    def __init__(self):
        pass


class Z:
    a = {}

    def __init__(self):
        self.b = 0


class A:
    a = dict()


def get_dict():
    return dict()


class B:
    a = get_dict()


def get_dict_2():
    return {}


class C:
    a = get_dict_2()


check(X) # X 35769728 35769728 35769728 True
check(Y) # Y 35769584 35769584 35769584 True
check(Z) # Z 35768864 35768864 35768864 True
check(A) # A 35816504 35816504 35816504 True
check(B) # B 35816720 35816720 35816720 True
check(C) # C 35768072 35768072 35768072 True





