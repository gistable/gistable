from random import randint
from itertools import islice


def random_sample(sample_size, items):
    """Maintain an evenly distributed random sample of a population of
    unknown size
    The Reservoir Sampling Algorithm
    (http://gregable.com/2007/10/reservoir-sampling.html)
    """
    items = iter(items)
    sample = list(islice(items, sample_size))
    yield sample
    for num, item in enumerate(items, start=sample_size):
        try:
            sample[randint(0, num)] = item
        except IndexError:
            pass
        yield sample

for i in random_sample(10, xrange(10000)):
    print i
