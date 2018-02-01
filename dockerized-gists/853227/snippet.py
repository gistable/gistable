from threading import Timer

class SuicidalKey(object):
    """
    >>> k = SuicidalKey("asdf",30)
    >>> k.key
    'asdf'
    >>> # Before 30 seconds are up
    >>> k.reset_expiration(30)
    >>> # Wait 30 seconds
    >>> k.key
    None
    """
    def __init__(self, key, expiration_time=300):
        self.key = key
        self.__expire_timer = Timer(0,None)
        self.reset_expiration(expiration_time)
    def __expire_key(self):
        self.key = None
    def reset_expiration(self, expiration_time=300):
        if self.key:
            self.__expire_timer.cancel()
            self.__expire_timer = Timer(expiration_time, self.__expire_key)
            self.__expire_timer.start()
