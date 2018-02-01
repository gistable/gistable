from collections import namedtuple

TableEntry = namedtuple('Element', 'hash key value')
class HashTable(object):
    DEFAULT_SIZE = 8
    EMPTY_VALUE = TableEntry(None, None, None)
    DELETED_VALUE = TableEntry(None, None, None)
    LOAD_FACTOR = 2 / 3
    MIN_FACTOR = 1 / 3

    def __init__(self):
        self.container = [self.EMPTY_VALUE] * self.DEFAULT_SIZE
        self.size = 0
        self.deleted_size = 0
        self.container_size = self.DEFAULT_SIZE
    
    def __len__(self):
        return self.size
    
    def __contains__(self, key):
        try:
            _ = self.get(key)
            return True
        except KeyError:
            return False

    def _resize(self):
        old_container = self.container
        old_size = self.size
        self.container_size = int(old_size // self.MIN_FACTOR)
        self.container = [self.EMPTY_VALUE] * self.container_size
        self.size = 0
        self.deleted_size = 0
        for element in old_container:
            if element is not self.EMPTY_VALUE and element is not self.DELETED_VALUE:
                self.set(element.key, element.value)

    def __repr__(self):
        tokens = []
        for element in self.container:
            if element is not self.EMPTY_VALUE and element is not self.DELETED_VALUE:
                tokens.append("{0} : {1}".format(element.key, element.value))
        return "{" + "\n".join(tokens) + "}"

    def _get_entry(self, key):
        """ Return (E0,E1) where E0 is the value or EMPTY_VALUE
        E1 is the index where it was found or if E0 is
        EMPTY_VALUE then the next insert index for the given key
        """
        key_hash = hash(key)
        root_index = key_hash
        for offset in range(self.container_size):
            index = (root_index + offset) % self.container_size
            element = self.container[index]
            if element is self.EMPTY_VALUE \
                or element.hash == key_hash and element.key == key:
                return (element, index)
        raise KeyError

    def set(self, key, value):
        entry, index = self._get_entry(key)
        self.container[index] = TableEntry(hash(key), key, value)
        if entry is self.EMPTY_VALUE:
            self.size += 1
        if (self.deleted_size + self.size) / self.container_size > self.LOAD_FACTOR:
            self._resize()
    
    def __setitem__(self, key, value):
        self.set(key, value)

    def get(self, key):
        entry, _ = self._get_entry(key)
        if entry is self.EMPTY_VALUE:
            raise KeyError('Key {0} not in hash table'.format(key))
        else:
            return entry.value
            
    def __getitem__(self, key):
        return self.get(key)

    def delete(self, key):
        entry, index = self._get_entry(key)
        if entry is self.EMPTY_VALUE:
            raise KeyError('Key {0} not in hash table'.format(key))
        else:
            self.container[index] = self.DELETED_VALUE
            self.size -= 1
            self.deleted_size += 1
    
    def __delitem__(self, key):
        self.delete(key)
