# -*- coding:utf8 -*-

u"""
函数apply的时候，传入的数据叫做arguments
arguments分为两种传入方式，按位置positional，按关键字keywords

函数define的时候，指定的参数列表叫做params，对这个列表的描述，叫做params spec，简称spec
"""

import inspect


class Arguments(object):
    def __init__(self, pos, key):
        u"""
        :param pos: 位置参数，必须是list-like
        :param key: 关键字式的参数，必须是dict-like
        """
        self.pos = list(pos)
        assert isinstance(key, dict)
        self.key = key

    def conform_to(self, spec):
        u"""判断当前的arguments是否符合parameter

        可能的情况有一下几种：
        1. spec所规定的没有满足，且不存在spec所规定不允许的，此时不能开始调用。此时调用会出现参数提供不足的错误
        2. spec所规定的没有满足，但存在spec所规定不允许的。此时开始调用，会报错
        3. spec所规定的已满足，且不存在spec所规定不允许的。此时可以开始正常调用，不会因参数而报错
        4. spec所规定的已满足，同时存在spec所规定不允许的。此时开始调用，会报错

        此函数不考虑spec所不允许的，也就是：
        case 1: 返回False
        case 2: 返回False
        case 3: 返回True
        case 4: 返回True

        等到后续的调用环节，再报错
        """
        # TODO: 检查spec所不允许的并及时raise
        if spec.defaults:
            requireds = spec.args[:-len(spec.defaults)]
        else:
            requireds = spec.args
        rest = requireds[len(self.pos):]
        return all([(r in self.key) for r in rest])

    def pass_to(self, func):
        u"""把arguments传入函数func"""
        return func(*self.pos, **self.key)

    def supply_with(self, other):
        u"""把新argument填到原有的argument里
        
        注意顺序
        a.supply_with(b) 与 b.supply_with(a) 有区别，pos参数的顺序不同
        """
        assert isinstance(other, Arguments)
        assert self is not other  # 因为根本不需要这样神奇的操作
        d = dict(self.key)
        d.update(other.key)
        return Arguments(self.pos + other.pos, d)

    def __str__(self):
        return '*{0}, **{1}'.format(self.pos, dict(self.key))


class Curried(object):
    def __init__(self, func, params, args):
        assert callable(func)
        self.func = func
        self.params = params
        self.args = args

    def __call__(self, *args, **kwargs):
        args = Arguments(args, kwargs)
        n_args = self.args.supply_with(args)
        if n_args.conform_to(self.params):
            return n_args.pass_to(self.func)
        else:
            return Curried(self.func, self.params, n_args)

    def __str__(self):
        return '<curried func={0}, args={1}, params={2}>'.format(self.func, self.args, self.params)

    @classmethod
    def is_type(cls, obj):
        return isinstance(obj, cls)

    @classmethod
    def assert_type(cls, obj):
        assert isinstance(obj, cls)


def curry(f):
    return Curried(f, inspect.getargspec(f), Arguments([], {}))


if __name__ == '__main__':
    # 仅使用位置参数，且不带默认值的情况
    def f(a, b):
        print a, b

    # print curry(f)
    # print curry(f)(1)
    # print curry(f)(1)(2)
    curry(f)(1)(2)
    curry(f)(1, 2)
    # curry(f)(1, 2, 3)(2)

    # 必须是函数式，每一次补充参数都返回新的函数对象
    cf = curry(f)
    assert cf is not cf(1)

    # 仅使用位置参数，但带有默认值的情况
    @curry
    def f1(a, b, c=3):
        print a, b, c

    Curried.assert_type(f1(1))
    assert None is f1(1)(2)
    assert None is f1(1, 2)
    assert None is f1(1, 2, 3)
    assert None is f1(1)(2, 3)
    
    # 仅有keyword方式调用，且不带默认值的情况
    @curry
    def f2(a, b, c):
        print a, b, c

    assert None is f2(a=1)(b=2)(c=3)
    assert None is f2(a=1, b=2)(c=3)
    assert None is f2(b=2, c=3)(a=1)
    assert None is f2(a=1, c=3)(b=2)
    assert None is f2(a=1, b=2, c=3)
    Curried.assert_type(f2(a=1))
    Curried.assert_type(f2(a=1, c=3))

    # 仅有keyword方式调用，且带默认值的情况
    @curry
    def f3(a, b, c=3, d=4):
        print a, b, c, d

    f3(a=1)(b=2)
    f3(b=2)(a=1)
    f3(a=1, b=2)
    f3(a=1)(b=2, c=3)
    f3(a=1, c=3)(b=2)
    f3(a=1, b=2, c=3, d=4)

    # 混合positional和keyword方式调用

    @curry
    def f4(a, b, c, d):
        print a, b, c, d

    f4(1)(b=2)(c=3)(d=4)
    f4(b=2)(c=3)(d=4)(1)
    f4(1, 2)(c=3)(d=4)
    f4(1, 2, 3)(d=4)

    # 混合方式调用，带有默认值

    @curry
    def f5(a, b, c, d=4, e=5):
        print a, b, c, d, e

    f5(1)(b=2)(c=3)
    f5(1, 2)(c=3)
    f5(c=3, d=4)(1, 2)
    f5(1, 2)(c=3, e=5)


    # 会出错的情况

    @curry
    def f6(a, b, c, d=4):
        print a, b, c, d

    # f6(1, 2, 3, 4, 5)    # 一次给出的参数太多
    # f6(1, 2, 3, z=None)  # 有不存在的参数
    f6(1, 2)(z=None)       # 此时是不会报错的，只有最终调用的时候会报错。这个行为不利于调试，考虑改掉

    # 支持接受按位置可变参数的函数

    @curry
    def f7(a, b, c, *args):
        print a, b, c, args

    f7(1)(2)(3)
    f7(1, 2)(3)
    f7(1, 2)(3, 4, 5)
    f7(1, 2, 3, 4, 5)

    # 支持接受按keyword可变参数的函数

    @curry
    def f8(a, b, c, **kwargs):
        print a, b, c, kwargs

    f8(1, x=0)(2, y=0)(3, z=0)
    f8(1, 2)(x=0, y=0, z=0)(3)
    f8(1, 2, 3, x=0, y=0, z=0)

    # 支持两种可变参数的函数

    @curry
    def f9(a, b, c, *args, **kwargs):
        print a, b, c, args, kwargs

    f9(1, x=0)(2, y=0)(3, 4, 5, z=0)
    f9(1, 2, 3, 4, 5, x=0, y=0, z=0)

    # 全支持
    # 允许各种特性同时存在:
    # + *args
    # + **kwargs
    # + defaults
    # + 按位置传入
    # + 按keyword传入

    @curry
    def f10(a, b, c=3, *args, **kwargs):
        print a, b, c, args, kwargs

    f10(1)(2)
    f10(1)(2, 3)
    f10(1, 2)
    f10(1, 2, 3)
    f10(1, 2, 3, 4)
    f10(1)(2, 3, 4)
    f10(1, x=0)(2, y=0, z=0)
    f10(1, x=0)(2, 3, 4, 5, y=0)
    f10(x=0, y=0, z=0)(1)(2)
    f10(x=0, y=0, z=0)(1)(2, 3, 4)

