# Helper class for statistics
# see: http://www.johndcook.com/blog/standard_deviation/
class Stats:
    """ Uses Welford's method to calculate stats.
        Assumes positive values.
        It's not thread safe

        stats = Stats("ConnectionTimeStats")
        stats.add(0.223)
        stats.add(1.343)
        print stats
    """
    def __init__(self, name="Stats"):
        self.name = name
        self.clear()

    def clear(self):
        self._count = 0
        self._min, self._max = float("inf"), 0.0
        self._oldm, self._newm = 0.0, 0.0
        self._olds, self._news = 0.0, 0.0

    def add(self, value):
        fvalue = float(value)
        self._count += 1
        self._max = max(self._max, fvalue)
        self._min = min(self._min, fvalue)
        if self._count == 1:
            self._oldm = self._newm = fvalue
            self._olds = 0.0
        else:
            self._newm = self._oldm + (fvalue - self._oldm) / float(self._count)
            self._news = self._olds + (fvalue - self._oldm) * (fvalue - self._newm)
            self._oldm = self._newm
            self._olds = self._news
    
    def count(self):
        return self._count

    def max(self):
        return self._max

    def min(self):
        return self._min

    def mean(self):
        return self._newm if self._count > 0 else 0.0

    def variance(self):
        return self._news / float(self._count - 1) if self._count > 1 else 0.0

    def std(self): # standard derivation
        import math
        return math.sqrt(self.variance())

    def __str__(self):
        return "%s: count %d min %.2f max %.2f mean %.2f (std dev %.3f variance %.2f)" %  (self.name, self.count(), self.min(), self.max(), self.mean(), self.std(), self.variance())
