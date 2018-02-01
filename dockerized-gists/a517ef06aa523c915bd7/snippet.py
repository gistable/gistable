from itertools import chain

class JsonFlatten:
    """Flattens nested dictionaries into a flat key/value mapping.

    This encoding is designed to be used with DictVectorizer

    See also
    --------
    :class:`sklearn.feature_extraction.DictVectorizer` to pass for
    subsequent processing
    """
    def _flattendict(self, d, prefix='', sep='/'):
        if isinstance(d, dict):
            if prefix:
                prefix += sep
            return chain(*(self._flattendict(v, prefix+k, sep)
                           for k, v in d.iteritems()))
        elif isinstance(d, list):
            if prefix:
                prefix += sep
            return chain(*(self._flattendict(v, prefix+str(k), sep)
                           for k, v in enumerate(d)))
        else:
            return (prefix, d),

    def transform(self, d, prefix='', sep='/'):
        """Transform nested dict into flat feature->value dict

        """
        return dict(self._flattendict(d, prefix, sep))

    def _insert_keyvalue(self, keys, v, d):
        for i, k in enumerate(keys[:-1]):
            if k not in d:
                if k.isdigit():
                    k = int(k)
                    d.append(None)
                if keys[i+1].isdigit():
                    d[k] = []
                else:
                    d[k] = {}
            d = d[k]
        if keys[-1].isdigit():
            d.append(v)
        else:
            d[keys[-1]] = v

    def inverse_transform(self, d, sep="/"):
        """Transform flat dictionary back to nested dictionary format
        """
        r = dict()
        for key in sorted(d):
            self._insert_keyvalue(key.split(sep), d[key], r)
        return r
