from functools import reduce
import re


_TYPES = {'string': str, 'int': int, 'object': dict, 'array': list,
          'bool': bool, 'null': type(None)}

_OPS = {'$eq': lambda s, d: s == d,
       '$gt': lambda s, d: d > s,
       '$gte': lambda s, d: d >= s,
       '$lt': lambda s, d: d < s,
       '$lte': lambda s, d: d <= s,
       '$ne': lambda s, d: s != d,
       '$in': lambda s, d: s in d,
       '$nin': lambda s, d: s not in d,
       '$or': lambda s, d: any(match(s_, d) for s_ in s),
       '$and': lambda s, d: all(match(s_, d) for s_ in s),
       '$not': lambda s, d: not match(s, d),
       '$nor': lambda s, d: not any(match(s_, d) for s_ in s),
       '$exists': lambda s, d: s in d,
       '$type': lambda s, d: type(d) == _TYPES[s],
       '$mod': lambda s, d: d % s[0] == s[1],
       '$regex': lambda s, d: re.search(s, d),
       '$where': lambda s, d: eval(s)(d),  # /!\ this is totally unsafe, beware
       '$all': lambda s, d: all(match(s, d_) for d_ in d),
       '$elemMatch': lambda s, d: any(match(s, d_) for d_ in d),
       '$size': lambda s, d: len(d) == s,
       '$bitsAllSet': lambda s, d: d & s == s,
       '$bitsAnySet': lambda s, d: d & s != 0,
       '$bitsAllClear': lambda s, d: d & s == 0,
       '$bitsAnyClear': lambda s, d: d & s != s,
      }

def _cast(f):
    try:
        return int(f)
    except ValueError:
        return f

def match(query, data):
    """Matches `data` against the mongoDB-style `query`.

    It does not check for compatible types so if query is malformated it may
    throw an error or silently match weirdly. Does not support text-search nor
    geospatial query selectors and the `$where` operator accepts a python
    lambda expression (as string), not javascript.
    See https://docs.mongodb.com/manual/reference/operator/query/ for more
    documentation.
    """

    return (query == data if type(query) in set(_TYPES.values()) - {dict}
            else all((_OPS[f](s, data) if f in _OPS
                         else match(s, reduce(lambda o, a: o[_cast(a)],
                                              f.split('.'), data)))
                     for f, s in query.items()))