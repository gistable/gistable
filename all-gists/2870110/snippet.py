class trie(object):
    MAX_SUGGEST = 10
    __slots__ = ('children', 'freq', 'name', '_top')

    def __init__(self):
        self.children = defaultdict(trie)
        self.freq = 0
        self.name = None
        self._top = None

    def __getitem__(self, suffix):
        node = self
        for letter in suffix:
            node = node.children[letter]
        return node

    @property
    def top(self):
        if self._top is None:
            self._top = self.compute_top()
        return self._top

    def compute_top(self):
        candidates = []
        for letter, child in self.children.items():
            candidates.extend(child.top)
        if self.name is not None:
            candidates.append((self.freq, self.name))
        candidates.sort(reverse=True)
        return candidates[:self.MAX_SUGGEST]

    def insert(self, freq, key, name):
        node = self[key]
        node.freq += freq
        node.name = name

    def walk(self, closure, prefix=None):
        prefix = prefix or self.name or ''
        closure(prefix, self.top)
        for letter, child in self.children.items():
            child.walk(closure, prefix + letter)

    def __repr__(self):
        return '<trie %s %d len(children)=%d>' % (self.name, self.freq, len(self.children))