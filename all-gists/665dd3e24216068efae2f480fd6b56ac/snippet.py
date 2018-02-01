class Person:
    def __init__(self):
        pass

    def _single(self):
        print "single"

    def __double(self):
        print "double"

p = Person()
print(dir(p))           # ['_Person__double', '__doc__', '__init__', '__module__', '_single']
p._single()             # single
p._Person__double()     # double
p.__double()            # AttributeError: Person instance has no attribute '__double'
