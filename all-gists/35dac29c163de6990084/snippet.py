import re

class _R(type):
    def __div__(self, regex):
        return R(regex)

class R(object):
    __metaclass__ = _R

    def __init__(self, regex):
        self._regex = re.compile(regex)

    def __div__(self, s):
        return RegexOperation(self._regex, s)

class RegexOperation(object):
    def __init__(self, regex, search):
        self._regex = regex
        self._search = search

    def __len__(self):
        return self._regex.search(self._search) is not None

    def search(self):
        match =  self._regex.search(self._search)
        if match is not None:
            return match.groups()

    def __mod__(self, replacement):
        return self._regex.sub(replacement, self._search)

    def __iter__(self):
        return iter(self._regex.findall(self._search))


rgx = '([0-9]+)'
print list(R/rgx/'123')
print (R/rgx/'1234').search()
print bool(R/rgx/'1234')
print bool(R/rgx/'abc')
print R/rgx/'123bar' % 'foo'