import functools

class memoize(object):
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        return self.cache_get(args, lambda: self.func(*args))
    def __get__(self, obj, objtype):
        return self.cache_get(obj, lambda: self.__class__(functools.partial(self.func, obj)))
    def cache_get(self, key, gen_callback):
        try:
            return self.cache[key]
        except KeyError:
            self.cache[key] = gen_callback()
            return self.cache[key]

class Adder(object):
    @memoize
    def add(self, arg1, arg2):
        print 'CALCULATING', arg1, '+', arg2
        return arg1 + arg2


@memoize
def subtract(arg1, arg2):
    print 'CALCULATING', arg1, '-', arg2
    return arg1 - arg2

def main():
    print subtract(10, 5)
    print subtract(10, 5)

    adder1 = Adder()
    adder2 = Adder()
    print adder1.add(5, 5)
    print adder1.add(5, 5)
    print adder2.add(5, 5)
    print adder2.add(5, 5)

if __name__ == '__main__':
    main()