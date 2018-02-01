"""
The Pool module provides some classes for managing a fixed-size thread-safe pool of functionally identical objects. One use for this is database connections, which tend to take awhile to create.

Pool
class that manages the pool of objects.

Constructor
class used to create new instances of items in the Pool.

For more details, use pydoc or read the docstrings in the code.

Credits : Andy Dustman
(Note: I just extracted the code from the Wayback Machine in order to find it more easily, but I didn't touch that code, all the credits goes to Andy Dustman !)

Version : 0.0.0, aka "Probably the first, last, and only release."
Released: 2002-06-30 00:00 UTC 
Stability: Perfect in every way
Original source : http://web.archive.org/web/20070610080245/http://dustman.net/andy/python/Pool/0.0.0/Pool.py
"""

from Queue import Queue, Full, Empty

class Pool(Queue):

    """Manage a fixed-size pool of reusable, identical objects."""
    
    def __init__(self, constructor, poolsize=5):
        Queue.__init__(self, poolsize)
        self.constructor = constructor

    def get(self, block=1):
        """Get an object from the pool or a new one if empty."""
        try:
            return self.empty() and self.constructor() or Queue.get(self, block)
        except Empty:
            return self.constructor()
        
    def put(self, obj, block=1):
        """Put an object into the pool if it is not full. The caller must
        not use the object after this."""
        try:
            return self.full() and None or Queue.put(self, obj, block)
        except Full:
            pass


class Constructor:

    """Returns a constructor that returns apply(function, args, kwargs)
    when called."""

    def __init__(self, function, *args, **kwargs):
        self.f = function
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return apply(self.f, self.args, self.kwargs)