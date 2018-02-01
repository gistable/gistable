import jsonpickle
import domain

"""
Based on the premise that any object can be identified by its class name and
a the value of a unique attribute (primary key) which is here reffered to as the identity
"""

def make_attribute_key(obj,attribute):
    """
    Returns a key for a given attribute/property of an object
    """
    basic_key = _make_basic_key(obj.__class__.__name__, obj.get_identity())
    return basic_key + attribute

def exists(db, class_name, identity):
    """
    Checks if a specific object exists in the redis store
    """
    result_keys = keys(db,class_name, identity)
    return True if len(result_keys) else False

def keys(db, class_name, identity):
    """
    Returns all keys for a given object
    """
    pattern = _make_key_pattern(class_name, identity)
    return db.keys(pattern)

def set(db, k, v):
    db.set(k,jsonpickle.encode(v))

def get(db,k):
    return jsonpickle.decode(db.get(k))

def mset(db, kv_dict):
    for k,v in kv_dict.iteritems():
        kv_dict[k] = jsonpickle.encode(v)
    db.mset(kv_dict)

def mget(db, keys):
    return [jsonpickle.decode(each) for each in db.mget(keys)]

def save(db, obj):
    mset(db, _make_pairs(obj))

def multisave(db, objs):
    """
    Saves multiple objects in one operation using a mset
    """
    pairs = {}
    for each in objs:
        pairs.update(_make_pairs(each))
    mset(db, pairs)

def delete(db, obj):
    [db.delete(each) for each in keys(db, obj.__class__.__name__, obj.get_identity())]


def read(db, class_name, identity):
    obj = getattr(domain, class_name)()
    result_keys = keys(db, class_name, identity)
    results = mget(db, result_keys)
    [setattr(obj, _extract_attribute(k), v) for k,v in zip(result_keys, results)]
    return obj

def read_attribute(db, class_name, identity, attrib):
    basic_key = _make_basic_key(class_name, identity)
    return get(db, basic_key + attrib)

""" Privates for key building"""

def _extract_attribute(key):
    return key.split(_sep())[-1]

def _sep():
    return '::'

def _make_basic_key(class_name, identity):
    return 'qackle' + _sep() + class_name + _sep() + identity + _sep()

def _make_key_pattern(class_name, identity):
    return _make_basic_key(class_name, identity) + '*'


""" Privates for object attributes"""

def _get_attributes(obj):
    return [each for each in dir(obj) if not each.startswith('_') and not callable(getattr(obj, each))]

def _make_pairs(obj):
    """
    Returns a dict where the keys are keys that denote an object property and value is the value
    of that property
    """
    attributes = _get_attributes(obj)
    pairs = {}
    for each in attributes:
        pairs[make_attribute_key(obj, each)] = getattr(obj, each)
    return pairs