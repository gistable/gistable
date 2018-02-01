from __future__ import print_function

try:
    from itertools import imap, izip, islice, count, cycle
except ImportError:
    # py3k
    imap = map
    izip = zip
    from itertools import (
        islice,
        count,
        cycle,
        )
    from functools import reduce


# def fizzbuzz():
#     return imap(lambda seq: reduce(lambda x, y: x or y, seq),
#                 izip(cycle(["fizzbuzz"] + [None] * 14),
#                      cycle(["fizz"] + [None] * 2),
#                      cycle(["buzz"] + [None] * 4),
#                      imap(str, count())))


class FizzBuzz(object):
    def __init__(self, *args, **kw):
        self.mapping = dict(*args, **kw)

    def __getitem__(self, key):
        return self.mapping[key]

    def __setitem__(self, key, val):
        self.mapping[key] = val

    def __delitem__(self, key):
        del self.mapping[key]

    def __iter__(self):
        return self.mapping.__iter__()

    def __call__(self):
        seqs = []
        for key in sorted(self.mapping.keys(), reverse=True):
            seqs.append(cycle([self.mapping[key]] + [None] * (key - 1)))
        seqs.append(imap(str, count()))
        return imap(lambda seq: reduce(lambda x, y: x or y, seq), izip(*seqs))


fizzbuzz = FizzBuzz()
fizzbuzz[3] = "Fizz"
fizzbuzz[5] = "Buzz"
fizzbuzz[15] = "FizzBuzz"
for n in islice(fizzbuzz(), 1, 100):
    print(n)
