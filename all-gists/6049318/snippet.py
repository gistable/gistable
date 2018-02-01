
def main():
    testobj_0 = MemoMethods('test0')
    testobj_1 = MemoMethods('test1')
    wrong0 = testobj_0.foo_borked
    right0 = testobj_0.foo_fixed
    wrong1 = testobj_1.foo_borked
    right1 = testobj_1.foo_fixed

    # this is the bug, wrong0's method is run with test1 as self
    assert 'test1 says i am borked'  == wrong0("i am borked")
    assert 'test0 says i am correct' == right0("i am correct")
    assert 'test1 says i am borked'  == wrong1("i am borked")
    assert 'test1 says i am correct' == right1("i am correct")


class memoize_borked(object):
    '''memoize decorator'''
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __get__(self, obj, type=None):
        self.obj = obj
        return self

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(self.obj, *args)
            self.cache[args] = value
            return value




class memoize(object):
    '''memoize descriptor'''
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, type=None):
        return self.memoize_inst(obj, self.func)

    class memoize_inst(object):
        def __init__(self, inst, fget):
            self.inst = inst
            self.fget = fget

            self.cache = {}

        def __call__(self, *args):
            # if cache hit, done
            if args in self.cache:
                return self.cache[args]
            # otherwise populate cache and return
            self.cache[args] = self.fget(self.inst, *args)
            return self.cache[args]



class MemoMethods(object):

    def __init__(self, inst_label):
        self.inst_label = inst_label

    @memoize_borked
    def foo_borked(self, thing):
        return "{} says {}".format(self.inst_label, thing)

    @memoize
    def foo_fixed(self, thing):
        return "{} says {}".format(self.inst_label, thing)


if __name__ == '__main__':
    main()
