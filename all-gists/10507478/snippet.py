import operator
from pprint import pprint

def is_dict(d):
    return isinstance(d, dict)
    
def get(c, k, default=None):
    try:
        return c[k]
    except (IndexError, KeyError, TypeError):
        return default

def get_in(c, key_path, default=None):
    def _getter(c, key):
        if c is default:
            return c
        return get(c, key, default)
    return reduce(_getter, key_path, c)

def assoc(d, k ,v):
    if d is None:
        d = {}
    d[k] = v
    return d

def assoc_in(d, key_path, v):
    if not key_path:
        raise ValueError("Cannot provide empty key path")
    key, rest = key_path[0], key_path[1:]
    if not rest:
        return assoc(d, key, v)
    else:
        return assoc(d, key, assoc_in(get(d, key), rest, v))

def merge_with(fn, *dicts):
    def _merge(d1, d2):
        for k, v in d2.iteritems():
            if k in d1:
                d1[k] = fn(d1[k], v)
            else:
                d1[k] = v
        return d1
    return reduce(_merge, dicts, {})

def deep_merge_with(fn, *dicts):
    def _merge(d1, d2):
        for k, v in d2.iteritems():
            if k in d1:
                if is_dict(d1[k]) and is_dict(v):
                    d1[k] = _merge(d1[k], v)
                else:
                    d1[k] = fn(d1[k], v)
            else:
                d1[k] = v
        return d1
    return reduce(_merge, dicts, {})

def expand_key(key, value):
    path = key.split(".")
    return assoc_in({}, path, value)

def expand_keys(d):
    expanded = [expand_key(k, v) for k, v in d.iteritems()]
    acc = {}
    for exp in expanded:
        acc = deep_merge_with(lambda _, v: v, acc, exp)
    return acc

query = {
    "query.filtered.query.bool.should": [
        {
            "query_string": {
                "default_field": "_all",
                "query": "keywords"
            },
        },
        {
            "multi_match": {
                "query": "123",
                "type": "most_fields",
                "fields": "derp"
            }
        }
    ],
    "query.filtered.query.filter": []
}

pprint(expand_keys(query))
# {'query': {'filtered': {'query': {'bool': {'should': [{'query_string': {'default_field': '_all',
#                                                                         'query': 'keywords'}},
#                                                       {'multi_match': {'fields': 'derp',
#                                                                        'query': '123',
#                                                                        'type': 'most_fields'}}]},
#                                   'filter': []}}}}
