import collections

class Dict(collections.MutableMapping):
    def __init__(s, *args, **kwargs):
        s.data = dict(*args, **kwargs)
    def __getitem__(s, k): return s.data[k]
    def __setitem__(s, k, v): s.data[k] = v
    def __delitem__(s, k): del s.data[k]
    def __iter__(s): return iter(s.data)
    def __repr__(s): return repr(s.data)
    def __len__(s): return len(s.data)

class List(collections.MutableSequence):
    def __init__(s, *args, **kwargs):
        s.data = list(*args, **kwargs)
    def insert(s, k, v): s.data.insert(k, v)
    def __setitem__(s, k, v): s.data[k] = v
    def __getitem__(s, k): return s.data[k]
    def __delitem__(s, k): del s.data[k]
    def __len__(s): return len(s.data)
    def __repr__(s): repr(s.data)

class Set(collections.MutableSet):
    def __init__(s, *args, **kwargs):
        s.data = set(*args, **kwargs)
    def __contains__(s, v): return v in s.data
    def __iter__(s): return iter(s.data)
    def discard(s, v): s.data.discard(v)
    def __repr__(s): return repr(s.data)
    def __len__(s): return len(s.data)
    def add(s, v): s.data.add(v)
