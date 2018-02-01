"""A caseless dictionary implementation."""

from collections import MutableMapping


class CaselessDictionary(MutableMapping):

    """
    A dictionary-like object which ignores but preserves the case of strings.

    Example::

        >>> cdict = CaselessDictionary()

    Access is case-insensitive::

        >>> cdict['a'] = 1
        >>> cdict['A']
        1

    As is writing::

        >>> cdict['key'] = 123
        >>> cdict['KeY'] = 456
        >>> cdict['key']
        456

    And deletion::

        >>> del cdict['A']
        >>> 'a' in cdict
        False
        >>> 'A' in cdict
        False

    However, the case of keys is preserved (the case of overridden keys will be
    the first one which was set)::

        >>> cdict['aBcDeF'] = 1
        >>> sorted(list(cdict))
        ['aBcDeF', 'key']
    """

    def __init__(self, *args, **kwargs):
        self._dict = {}
        temp_dict = dict(*args, **kwargs)
        for key, value in temp_dict.iteritems():
            if isinstance(key, basestring):
                key = CaselessString.make_caseless(key)
            self._dict[key] = value

    def __getitem__(self, key):
        return self._dict[CaselessString.make_caseless(key)]

    def __setitem__(self, key, value):
        self._dict[CaselessString.make_caseless(key)] = value

    def __delitem__(self, key):
        del self._dict[CaselessString.make_caseless(key)]

    def __contains__(self, key):
        return CaselessString.make_caseless(key) in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)


class CaselessString(object):

    """A mixin to make a string subclass case-insensitive in dict lookups."""

    def __hash__(self):
        return hash(self.lower())

    def __eq__(self, other):
        return self.lower() == other.lower()

    def __cmp__(self, other):
        return self.lower().__cmp__(other.lower())

    @classmethod
    def make_caseless(cls, string):
        if isinstance(string, unicode):
            return CaselessUnicode(string)
        return CaselessStr(string)


class CaselessStr(CaselessString, str):
    pass


class CaselessUnicode(CaselessString, unicode):
    pass
