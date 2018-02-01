
from contextlib import contextmanager

class CaseContext(object):

    def __init__(self, that):
        self.that = that

    def when(self, *cases):
        for a in cases:
            if a != self.that:
                continue
            yield a
            break
        

@contextmanager
def case(that):
    yield CaseContext(that)

with case("mana") as that:
    for it in that.when("dollias"):
        print it
    for it in that.when("mana"):
        print it