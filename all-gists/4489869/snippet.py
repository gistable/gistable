In [2]: class C(object):
   ...:   def hi(self, k, d=dict()):
   ...:     d[k] = 1
   ...:     print d
   ...:

In [3]: c = C()

In [4]: c.hi(1)
{1: 1}

In [5]: c.hi(2)
{1: 1, 2: 1}

In [6]: d = C()

In [7]: d.hi(3)
{1: 1, 2: 1, 3: 1}

In [8]: