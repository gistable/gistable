def flatten(xs):
    for x in xs:
        if hasattr(x, "__iter__"):
            yield from flatten(x)
        else:
            yield x
