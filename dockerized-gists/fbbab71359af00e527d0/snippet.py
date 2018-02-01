class edict(dict):  # Similar to bunch, but less, and JSON-centric
    # based on class dotdict(dict):  # from http://stackoverflow.com/questions/224026/dot-notation-for-dictionary-keys
    
    __setattr__= dict.__setitem__  # TBD: support assignment of nested dicts by overriding this?
    __delattr__= dict.__delitem__

    def __init__(self, data):
        if type(data) in ( unicode, str ):
            data = json.loads( data)
    
        for name, value in data.iteritems():
            setattr(self, name, self._wrap(value))

    def __getattr__(self, attr):
        return self.get(attr, None)

    def _wrap(self, value):  # from class Struct by XEye '11 http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])  # recursion!
        else:
            if isinstance(value, dict):
                return edict(value)  # is there a relative way to get class name?
            else:
                return value

# optional handy member function(s): pretty-printer, ... left as an exercise for the reader...
# def subset(self, only_keys=[], exclude_keys=[], as='json', indent=2, separators=(',',':')):

# EOF