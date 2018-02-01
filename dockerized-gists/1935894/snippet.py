"""Simple example showing why using super(self.__class__, self) is a BAD IDEA (tm)"""

class A(object):
    def x(self):
        print "A.x"

class B(A):
    def x(self):
        print "B.x"
        super(B, self).x()

class C(B):
    def x(self):
        print "C.x"
        super(C, self).x()


class X(object):
    def x(self):
        print "X.x"

class Y(X):
    def x(self):
        print "Y.x"
        super(self.__class__, self).x()  # <- this is WRONG don't do it!

class Z(Y):
    def x(self):
        print "Z.x"
        super(self.__class__, self).x()  # <- this is WRONG don't do it!

if __name__ == '__main__':
    C().x()
    Z().x() # will cause 'RuntimeError: maximum recursion depth exceeded'
