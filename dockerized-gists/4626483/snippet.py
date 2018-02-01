import operator
def geometric_mean(iterable):
    return (reduce(operator.mul, iterable)) ** (1.0/len(iterable))