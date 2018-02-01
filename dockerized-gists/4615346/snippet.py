class CacheCallable(object):
    """Callable that cache results based on given arguments
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            return self.cache[args]
        except:
            result = self.func(*args)
            return self.cache.setdefault(args, result)


class CacheProxy(object):
    """Proxy that cache attributes
    """
    def __init__(self, target):
        object.__setattr__(self, 'target', target)
        object.__setattr__(self, 'cache', {})

    def __getattribute__(self, name):
        target = object.__getattribute__(self, 'target')
        cache = object.__getattribute__(self, 'cache')
        try:
            return cache[name]
        except KeyError:
            attr = getattr(target, name)
            return cache.setdefault(name, CacheCallable(attr)
                                    if callable(attr) else attr)

    def __setattr__(self, name, value):
        target = object.__getattribute__(self, 'target')
        cache = object.__getattribute__(self, 'cache')
        cache[name] = value
        setattr(target, name, value)



class SlowOriginal(object):
    def wait(self, seconds, preamble, frames, erase):
        """Block execution and display an animation while waiting.
        """
        import sys, time
        sys.stdout.write(' ')
        sys.stdout.write(preamble)
        for frame in frames:
            sys.stdout.write(frame)
            time.sleep(float(seconds)/len(frames))
            if erase:
                sys.stdout.write('\b'*len(frame))
        if erase:
            sys.stdout.write('\b'*(len(preamble)))

    @property
    def id(self):
        self.wait(3, 'waiting ', '-\|/'*6, True)
        return id(self)

    def query(self):
        self.wait(3, 'searching ', '............ ', False)
        return 'found'

    def countdown(self, seconds):
        frames = list(str(seconds - n) for n in xrange(seconds))
        self.wait(seconds, 't minus ', frames, True)
        return 'Take off!'

    def process(self):
        frames = ('load - ',
                  'init - ',
                  'run - ')
        self.wait(5, '', frames, False)
        return 'done'

original = SlowOriginal()
original.value = object()

proxy = CacheProxy(original)
#proxy.value = object()

for obj in (original, proxy):
    print 'obj =', obj
    print
    for n in xrange(2):
        print '\tobj.query()      =', obj.query()
        print '\tobj.process()    =', obj.process()
        print '\tobj.id           =', obj.id
        print '\tobj.countdown(5) =', obj.countdown(5)
        print '\t', '-'*80
    print
