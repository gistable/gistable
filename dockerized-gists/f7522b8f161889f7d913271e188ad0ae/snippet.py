class Point(object):
    
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self._x, self._y))

    def __sub__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return Point(self._x - other._x, self._y - other._y)

    def __rsub__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return other - self

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self._x + other._x, self._y + other._y)
        elif isinstance(other, QPoint):
            return Point(self._x + other.x(), self._y + other.y())
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Point):
            return Point(self._x + other._x, self._y + other._y)
        elif isinstance(other, QPoint):
            return Point(self._x + other.x(), self._y + other.y())
        return NotImplemented
