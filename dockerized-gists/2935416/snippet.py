class Future (object) :
    def __init__ (self, *args, **kwargs) :
        super (Future, self).__init__ (*args, **kwargs)

    def __nonzero__ (self) :
        return bool (self._data ())

    def __len__ (self) :
        return len (self._data ())

    def __setitem__ (self, key, value) :
        return self._data ().__setitem__ (key, value)
    
    def __getitem__ (self, key) :
        return self._data ().__getitem__ (key)

    def __str__ (self) :
        return self._data ().__str__ ()

    def __repr__ (self) :
        return self._data ().__repr__ ()

    def _data (self) :
        pass # load data


