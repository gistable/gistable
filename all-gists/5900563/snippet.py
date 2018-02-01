from robot.api import ExecutionResult, ResultVisitor
import math, re

class KeywordTimes(ResultVisitor):

    VAR_PATTERN = re.compile(r'^(\$|\@)\{[^\}]+\}(, \$\{[^\}]+\})* = ')

    def __init__(self):
        self.keywords = {}

    def end_keyword(self, keyword):
        name = self._get_name(keyword)
        if name not in self.keywords:
           self.keywords[name] = KeywordsTime(name)
        self.keywords[name].elapsedtimes += [keyword.elapsedtime]

    def _get_name(self, keyword):
        name = keyword.name
        m = self.VAR_PATTERN.search(name)
        if m:
           return name[m.end():]
        return name


class KeywordsTime(object):

    def __init__(self, name):
        self.name = name
        self.elapsedtimes = []

    @property
    def elapsed(self):
        return float(sum(self.elapsedtimes))/1000

    @property
    def calls(self):
        return len(self.elapsedtimes)

    @property
    def average_time(self):
        return round(float(self.elapsed)/self.calls, 3)

    @property
    def median_time(self):
        s = sorted(self.elapsedtimes)
        half = float(len(s)-1) / 2
        half_low = int(math.floor(half))
        half_high = int(math.ceil(half))
        return round(float(s[half_low]+s[half_high])/2000, 3)

    @property
    def variance(self):
        squares = [(float(i)/1000)**2 for i in self.elapsedtimes]
        return sum(squares)/len(squares)-(self.elapsed/self.calls)**2

    @property
    def standard_deviation(self):
        return round(self.variance**0.5, 3)

    def __cmp__(self, other):
        return other.elapsed - self.elapsed


if __name__ == '__main__':
    import sys
    resu = ExecutionResult(sys.argv[1])
    times = KeywordTimes()
    resu.visit(times)
    s = sorted(times.keywords.values())
    shown_keywords = 100
    print 'Total time (s) | Number of calls | avg time (s) | median time (s) | standard deviation (s) | Keyword name'
    for k in s[:shown_keywords]:
        print str(k.elapsed).rjust(14)+' | '+str(k.calls).rjust(15)+ ' | ' + \
                str(k.average_time).rjust(12) + ' | ' + str(k.median_time).rjust(15) + \
                ' | ' + str(k.standard_deviation).rjust(22) + (' | "%s"' % k.name)
    print 'Showing %d of total keywords %d' % (shown_keywords, len(times.keywords))
