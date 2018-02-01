class MidpointLruCache:
    def __init__(self, size, oldpercentage):
        self.size = size
        self.oldsize = size * oldpercentage / 100
        self.youngsize = size * (100 - oldpercentage) / 100

        self.youngitems = collections.OrderedDict()
        self.olditems = collections.OrderedDict()

    def __call__(self, func):
        def wrapper(arg):
            if arg in self.olditems:
                value = self.olditems[arg]
                del self.olditems[arg]
                self.olditems[arg] = value
            elif arg in self.youngitems:
                value = self.youngitems[arg]
                del self.youngitems[arg]
                self.olditems[arg] = value
            else:
                value = func(arg)
                self.youngitems[arg] = value

            if len(self.olditems) > self.oldsize:
                poparg,popvalue = self.olditems.popitem(False)
                self.youngitems[poparg] = popvalue

            while len(self.olditems)+len(self.youngitems) > self.size:
                self.youngitems.popitem(False)

            return value
        return wrapper