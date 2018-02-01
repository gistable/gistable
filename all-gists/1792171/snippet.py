import collections
import Queue

class MaxSizeDict(collections.MutableMapping):
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self.valdict = {}
        self.keyqueue = Queue.Queue()

    def __setitem__(self, key, value):
        self.valdict[key] = value
        self.keyqueue.put(key)
        while len(self.valdict) > self.maxsize:
            del self.valdict[self.keyqueue.get()]

    def __contains__(self, key):
        return key in self.valdict

    def __iter__(self):
        return iter(self.valdict)

    def __len__(self):
        return len(self.valdict)

    def __delitem__(self, k):
        raise NotImplemented

    def __getitem__(self, k):
        return self.valdict[k]

    def __str__(self):
        return str(self.valdict)

    def __repr__(self):
        return repr(self.valdict)
