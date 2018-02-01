# Memoize Example

class Pak(object):

    # Do not use @staticmethod here
    def memoize(key):
        def decfunc(f):
            def newfunc(self):
                if not hasattr(self, key):
                    setattr(self, key, f(self))
                else:
                    print "retrieve from mem"
                return getattr(self, key)
            return newfunc
        return decfunc

    @memoize('c')
    def getc(self):
        print "computing"
        return 1 + 1
        

p = Pak()


p.getc()
p.getc()
p.getc()
