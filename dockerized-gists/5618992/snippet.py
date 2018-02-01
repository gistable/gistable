# Passes https://gist.github.com/mrocklin/5722155

def groupby(f, coll):
    """ Group elements in collection by ``f`` """
    d = dict()
    for item in coll:
        key = f(item)
        if key not in d:
            d[key] = []
        d[key].append(item)
    return d
