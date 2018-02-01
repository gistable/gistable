import collections

class Trie(collections.MutableSet):
    def __init__(self, iterable=None):
        self.children = {}
        self.accepting = False
        if iterable is not None:
            for item in iterable:
                self.add(item)

    def add(self, word):
        """Add word to the trie, if not already present.
        
        Otherwise, do nothing.
        
        """
        if len(word) == 0:
            self.accepting = True
        else:
            head = word[0]
            tail = word[1:]
            if head not in self.children:
                self.children[head] = Trie()
            self.children[head].add(tail)

    def discard(self, word):
        """Remove word from the trie, if present.

        Otherwise, do nothing.

        """
        if len(word) == 0:
            self.accepting = False
        else:
            head = word[0]
            tail = word[1:]
            if head in self.children:
                child = self.children[head]
                child.discard(tail)
                for _ in child:
                    # Efficiently check if any items are present
                    break
                else:
                    # Child is empty, prune it
                    del self.children[head]

    def __contains__(self, word):
        if len(word) == 0:
            return self.accepting
        else:
            head = word[0]
            tail = word[1:]
            if head not in self.children:
                return False
            return tail in self.children[head]

    def __iter__(self):
        if self.accepting:
            yield ''
        for key, node in self.children.items():
            for word in node:
                yield key + word

    def __len__(self):
        result = 0
        for node in self.children.values():
            result += len(node)
        if self.accepting:
            result += 1
        return result

    def search(self, prefix):
        """Iterate over members of the trie starting with prefix."""
        if len(prefix) == 0:
            for item in self:
                yield item
        else:
            head = prefix[0]
            tail = prefix[1:]
            if head in self.children:
                child = self.children[head]
                for item in child.search(tail):
                    yield head + item