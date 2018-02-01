class Clonable(type):
    def __new__(cls, name, bases, body):
        __init__ = body['__init__']
        def init(s, *a, **kw):
            s.clone = lambda a=a, kw=kw: type(s)(*a, **kw)
            return __init__(s, *a, **kw)
        body['__init__'] = init
        return super().__new__(cls, name, bases, body)

class Estimator(metaclass=Clonable):
    pass

class Obj(Estimator):
    def __init__(s, x, y, *a, **kw):
        s.w, s.x, s.y, s.z = a, x, y, kw
    def __repr__(self):
        return 'Obj(x={self.x}, y={self.y})'.format(self=self)

if __name__ == '__main__':
    x = Obj('abc', 123)
    print(id(x), x)
    y = x.clone()
    print(id(y), y)
