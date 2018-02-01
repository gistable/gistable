#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#          MixinParent
#             |
#           Mixin    A
#             └--┐   |
#                  B


class A(object):
    def test(self):
        # super(A, self).test() #if put in, AttributeError: 'super' object has no attribute 'test'
        print 'A'


class MixinParent(object):
    def test(self):
        super(MixinParent, self).test() #if left out, A's test() method will not be called.
        print 'MixinParent'


class Mixin(MixinParent):
    def test(self):
        super(Mixin, self).test()
        print 'Mixin'


class B(Mixin, A):
    def test(self):
        super(B, self).test()
        print 'B'


b = B()
b.test()


# output:
# > A
# > MixinParent
# > Mixin
# > B
