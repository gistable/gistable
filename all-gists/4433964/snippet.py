#!/usr/bin/python
# encoding: utf-8

class Foo(object):
    def __init__(self):
        self._func = None

    def callDerivedFunc(self):
        self._func() # wrong    #这里实际上等于：Bar.hello(), hello是一个实例方法，需要传递一个实例才能调用。所以报错，应该改成：self._func(self)
        method = self._func
        method(self) # right    # 由于传递了一个实例self，相当于：Bar.hello(self)，所以可以成功调用

class Bar(Foo):
    def __init__(self):
        super(Foo, self).__init__()
        self._func = Bar.hello

    def hello(self):
        print 'Hello'

bar = Bar()
bar.callDerivedFunc()

