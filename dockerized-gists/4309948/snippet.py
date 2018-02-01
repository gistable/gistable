import UserDict

class Chainmap(UserDict.DictMixin):

    def __init__(self, *maps):
        self._maps = maps

    def __getitem__(self, key):
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)

    def key(self):
        l = []
        for mapping in self._maps:
            l+=mapping.keys()
        return l