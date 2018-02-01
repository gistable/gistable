class conduit(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def filter(self, predicate):
        return conduit(itertools.ifilter(predicate, self.iterator))

    def map(self, func):
        return conduit(itertools.imap(func, self.iterator))

    def sort(self, key):
        # sort has to evaluate the iterator
        return conduit(sorted(self.iterator, key=key))

    def __iter__(self):
        return iter(self.iterator)

    def to_list(self):
        return list(self)