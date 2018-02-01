import itertools as it

def sortandgroupby(data, **kwargs):
    return dict(map(lambda(k,v):(k,list(v)),it.groupby(sorted(data,kwargs),kwargs)))

print sortandgroupby(range(30),lambda x:mod(x,3))

