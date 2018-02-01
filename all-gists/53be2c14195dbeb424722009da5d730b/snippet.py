def dmerge(x, (k,v)):
    if k in x:
        dmerge(x[k], v.items()[0])
    else:
        x[k] = v 
    return x

def hdict_from_dict(src):
    return reduce(lambda x, y: dmerge(x, y), [hdict(k, v).items()[0] for k, v in src.items()], {})

def hdict(keys, value, sep="/"):
    return reduce(lambda v, k: {k: v}, reversed(keys.split(sep)), value)

data = {
    "a/b/c": 10,
    "a/b/d": 20,
    "a/e": "foo",
    "a/f": False,
    "g": 30 }

print("flat:", data)
print("tree:", hdict_from_dict(data))