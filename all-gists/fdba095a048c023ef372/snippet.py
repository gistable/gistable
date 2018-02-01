In [4]: class Foo(object):
   ...:     def __init__(self, func=None):
   ...:         if func:
   ...:             # Better validation is required
   ...:             self.execute = types.MethodType(func, self)
   ...:     def execute(self):
   ...:         print "Normal"
   ...:

In [5]: def execute(self):
   ...:     print "Injected"
   ...:

In [6]: f1 = Foo()

In [7]: f2 = Foo(func=execute)

In [8]: f1.execute()
Normal

In [9]: f2.execute()
Injected