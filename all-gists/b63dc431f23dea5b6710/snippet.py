from abc import ABCMeta, abstractmethod
import sys

# lets get one thing straight right out of the box:

def fail(e):
    import traceback
    with open("/tmp/tb", "w") as f:
        traceback.print_exc(e, f)

def win(s):
    print "win: %s" % str(s)

def debug(s, ref):
    with open("/tmp/debug-%s" % (ref),"w") as f:
      f.write(str(s))

# this is a type which will be wrapped around the return values of
# many of our functions. Its a bit of machinery which will let us hide
# away the bookeeping of handling errors, which allows us to more
# easily express much of the rest of the code through function composition.
class Either:
    __metaclass__ = ABCMeta

    @abstractmethod
    def fold(self, bad, good): return

    # apply a function to the contained value, if our value is Good.
    def map(self, f):
        return self.fold(lambda x: Bad(x), lambda x: Good(f(x)))

    # if our value is Good, apply a function to the contained value,
    # which returns an Either if our value is Bad just return it,
    # ignoring the function
    def bind(self, f):
        return self.fold(lambda x: Bad(x), f)

    def ap(self, f):
        return self.fold(lambda x: Bad(x),
                         lambda x: f.fold(lambda y: Bad(y),
                                          lambda f: Good(f(x))))

    def isGood(self):
        return self.fold(lambda x: False, lambda x: True)

    def orElse(self, other):
        return self if self.isGood() else other

    @classmethod
    def fromTry(k,block):
        try:
            v = block()
            return Good(v)
        except Exception as e:
            fail(e)
            return Bad(e)

    @classmethod
    def traverse(k, l, f):
        r = Good([])
        for x in l:
            xx = f(x)
            if xx.isGood():
                ra = r.a
                ra.append(xx.a)
                r = Good(ra)
            else:
                return xx

        return r

    @classmethod
    def traverseDict(k, d, f):
        r = Good({})
        for x in d:
            xx = f(x, d[x])
            if xx.isGood():
                ra = r.a
                ra[x] = xx.a
                r = Good(ra)
            else:
                return xx

        return r

class Bad(Either):
    def __init__(self, a):
        self.a = a

    def fold(self, bad, good):
        return bad(self.a)

    def __str__(self):
        return "Bad(%s)" % str(self.a)

class Good(Either):
    def __init__(self,a):
        self.a = a

    def fold(self, bad, good):
        return good(self.a)

    def __str__(self):
        return "Good(%s)" % str(self.a)

Either.register(Bad)
Either.register(Good)
