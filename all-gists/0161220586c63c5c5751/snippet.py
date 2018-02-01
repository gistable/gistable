# coding: utf-8
# 更多内容参见：https://en.wikibooks.org/wiki/Haskell/Fix_and_recursion

from functools import wraps, partial
import inspect


# 模拟call-by-name求值，注意并非Haskell中的惰性求值（此种求值手段还有待研究）
def lazy(func):
    if is_lazy(func):
        return func

    if inspect.isfunction(func):
        @wraps(func)
        def newfunc(*args, **kwargs):
            yield func(*args, **kwargs)
    else:
        newfunc = thunk(func)
    return newfunc


def is_lazy(obj):
    return inspect.isgenerator(obj)


# 简单的包装，模拟Haskell中的次程式
@lazy
def thunk(obj):
    return obj


# 递归地进行求值过程，对于完全应用的部分函数直接求值
def force_eval(t):
    if is_lazy(t):
        t = next(t, None)
        return force_eval(t)
    if isinstance(t, partial):
        func = t.func
        sig = inspect.signature(func)
        if len(sig.parameters) == len(t.args):
            return force_eval(t())
    return t if not is_lazy(t) else force_eval(t)


# 不动点
@lazy
def fix(func):
    # 这里只能手动控制求值，非常不方便
    func = force_eval(func)
    return partial(func, fix(func))


@lazy
def add(a, b):
    return force_eval(a) + force_eval(b)


add1 = lazy(partial(add, 1))


# Haskell中的const
@lazy
def const(a, _):
    return a


# Haskell中的seq
@lazy
def seq(a, b):
    force_eval(a)
    return b


# 递归元，注意函数中并没有显式递归。
@lazy
def factorial_step(func, n):
    func, n = force_eval(func), force_eval(n)
    if n == 1:
        return n
    return n * force_eval(func(n-1))


if __name__ == '__main__':
    print(
        "1 + 2 = {}".format(
        force_eval(add(lazy(1), 2))
        )
    )
    print(
        "const 8 _ = {}".format(
            force_eval(fix(partial(const, 8)))
        )
    )
    # 基于Ycombinator的递归
    print(
        "factorial(10) = {}".format(
            force_eval(
                force_eval(
                    fix(
                        factorial_step,
                    )
                )(10)
            )
        )
    )
    # print(force_eval(fix(lazy(add1))))  # 底元素，会导致栈溢出
