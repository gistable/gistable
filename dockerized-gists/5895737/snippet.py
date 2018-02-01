class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

# Sometimes need more flexibility --> use properties

class Point:
    def __init__(self, x, y):
        self._x, self._y = x, y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value