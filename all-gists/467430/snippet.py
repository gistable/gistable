class Fab(object):
    def __enter__(self):
        self._stack = []
        return self

    def __exit__(self, *args, **kwargs):
        print self._stack

    def __call__(self, *args):
        self._stack += args
        return self

def tmpl(self):
    print "tmpl\t", self
    return self

def listen(self, *args):
    print "listen\t", self
    return self

with Fab() as fab:
    (fab)\
        (listen, 0xFAB)\
            (r'^hello/$')(tmpl)\
                ( "hello, {{ self }}")\
            (r'(?P<what>\w+)/$')(tmpl)\
                ( "hello, {{ self.what }}")\
            (404)
