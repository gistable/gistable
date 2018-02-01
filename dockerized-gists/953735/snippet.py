'''
Usage: viz.py INPUT.csv [template.html] > OUTPUT.xhtml
'''

import re
import math
import logging
import datetime
import operator
from tornado import template

def average(series):
    sum, count = 0.0, 0
    for value in series:
        try:
            sum = sum + float(value)
            count += 1
        except:
            pass
    return sum / (count or 1)

def humanize(x, digits=3):
    '''
    - Incorporate number of digits. But how?
    - Incorporate intcomma
    '''
    a = abs(x)
    if   a < 1:      return '%0.3f' % x
    elif a < 10:     return '%0.2f' % x
    elif a < 100:    return '%0.1f' % x
    elif a < 100000: return '%0.0f' % x
    else:            return '%0.2e' % x

def intcomma(value):
    if type(value) != str: orig = str(int(value+0.5))
    else: orig = value
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return intcomma(new)

def uniq(iterator):
    hash = {}
    out = []
    for item in iterator:
        if not item in hash:
            hash[item] = 1
            out.append(item)
    return out

def _colornum(color):
    return (int(color[-6:-4], 16), int(color[-4:-2], 16), int(color[-2:], 16))

def gradient(x, ranges):
    '''gradient(0.4, ((-1, '#ff0000'), (0, '#ffffff'), (1, '#00ff00')))
    interpolates 0.4 between -1 - 0 - +1 and returns an in-between color
    as rgb(r,g,b)'''
    x = float(x)
    ranges = sorted(ranges, key=operator.itemgetter(0))
    if x <= ranges[0][0]: return ranges[0][1]
    if x >= ranges[-1][0]: return ranges[-1][1]
    for i, (start, color) in enumerate(ranges):
        if x <= start: break
    p = (x - ranges[i-1][0]) / (ranges[i][0] - ranges[i-1][0])
    a = _colornum(ranges[i-1][1])
    b = _colornum(ranges[i][1])
    color = tuple(int((a[c]*(1.0-p) + b[c]*p)) for c in (0,1,2))
    return 'rgb(%d,%d,%d)' % color

class Query:
    '''
    Usage:
        >>> from viz import Query
        >>> q = Query([{'a':1}, {'a':1}, {'a':3}])
        >>> q.filter(a=2)
        >>> q.freq('a', all='All')
    '''
    def __init__(self, data):
        self._filter = {}
        self._freq = {}
        self.data = data

    def freq(self, *columns, **options):
        key = tuple(columns) + tuple(options.items())
        if key in self._freq:
            return self._freq[key]

        all = options.get('all', None)
        result = {}
        if len(columns) > 1:
            for row in self.data:
                key = tuple(row.get(column, None) for column in columns)
                if not key is None:
                    result[key] = result.get(key, 0) + 1
                if all:
                    result[all] = result.get(all, 0) + 1
        else:
            column = columns[0]
            for row in self.data:
                key = row.get(column, None)
                if not key is None:
                    result[key] = result.get(key, 0) + 1
                if all:
                    result[all] = result.get(all, 0) + 1

        result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)
        self._freq[columns] = result
        return result

    def filter(self, **filter):
        keys = tuple(filter.items())
        if keys in self._filter:
            return self._filter[keys]

        result = []
        for row in self.data:
            match = True
            for key, value in keys:
                if row[key] != value:
                    match = False
                    break

            if match:
                result.append(row)

        self._filter[keys] = result
        return result

class Series:
    def __init__(self, data):
        self.value = []
        v = []

        sx, sy, sxx, sxy, syy = 0.0, 0.0, 0.0, 0.0, 0.0
        for i, value in enumerate(data):
            try:
                f = float(value)
                v.append(f)
                self.value.append(f)
                sx += i
                sy += f
                sxx += i*i
                syy += f*f
                sxy += i*f
            except:
                f = ''
                self.value.append(value)

        v.sort()
        self.min = min(v) if len(v) else 0
        self.max = max(v) if len(v) else 0
        self.mean = sum(v) / len(v) if len(v) else 0
        self.range = (self.max - self.min) or 1
        self.len = len(self.value)
        self._v = v
        if self.len > 0 and (sxx - sx*sx/self.len) > 0:
            self.growth = (sxy - sx*sy/self.len) / (sxx - sx*sx/self.len) * self.len
        else:
            self.growth = 0


    def quantile(self, q):
        p = float(q)*(len(self._v)-1)
        d = p - int(p)
        return self._v[int(p)]*(1.0-d) + self._v[int(p+1)]*d

    def correlate(self, series):
        n, sx, sy, sxx, sxy, syy = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        for i in xrange(min(len(self.value), len(series.value))):
            x = self.value[i]
            y = series.value[i]
            if type(x) == float and type(y) == float:
                sx += x
                sy += y
                sxx += x*x
                syy += y*y
                sxy += x*y
                n += 1
        if n > 0:
            varx = sxx - sx*sx/n
            vary = syy - sy*sy/n
            sd = (varx * vary)**0.5
            if sd > 0:
                return (sxy - sx*sy/n) / sd
        return 0

class Draw:
    @classmethod
    def show_attrs(cls, *args):
        attr = {}
        for arg in args: attr.update(arg)
        s = []
        for key, val in attr.iteritems():
            s.append('%s="%s"' % (key, val.replace('"', r'\"')))
        return ' '.join(s)


    sparkline_template = template.Template('''
    <rect x="{{ x }}" y="{{ y1 }}" width="{{ w }}" height="{{ y3-y1 }}" {{ cls.show_attrs(attr, {'stroke':'none'}) }} />
    <path d="{{ path }}" {{ cls.show_attrs(attr, {'fill': 'none'}) }} />
    '''.strip())

    @classmethod
    def sparkline(cls, x, y, w, h, data, attr={}):
        path = []
        y1 = y + h*(data.max - data.quantile(0.90)) / data.range
        y3 = y + h*(data.max - data.quantile(0.10)) / data.range
        for i, value in enumerate(data.value):
            if type(value) == float:
                vx = x + w*float(i)/(data.len-1)
                vy = y + h*(1.0 - (float(value) - data.min)/data.range)
                path.append('%s %f %f' % ('L' if i else 'M', vx, vy))

        path = ' '.join(path)
        return cls.sparkline_template.generate(**locals())

    boxplot_template = template.Template('''
    <line x1="{{ x0 }}" x2="{{ x4 }}" y1="{{ y + h*0.5 }}" y2="{{ y + h*0.5 }}" {{ cls.show_attrs(attr) }}/>
    <rect x="{{ x1 }}" y="{{ y + h*0.1 }}" width="{{ x3 - x1 }}" height="{{ h*0.8 }}" {{ cls.show_attrs(attr) }} />
    <line x1="{{ x2 }}" x2="{{ x2 }}" y1="{{ y + h*0.1 }}" y2="{{ y + h*0.9 }}" {{ cls.show_attrs(attr) }}/>
    '''.strip())

    @classmethod
    def boxplot(cls, x, y, w, h, data, attr={}, params={}):
        start = params.get('min', data.min)
        finish = params.get('max', data.max)
        range = (finish - start) or 1
        x0    = x + w*(data.min             - start) / range
        x1    = x + w*(data.quantile(0.25)  - start) / range
        x2    = x + w*(data.quantile(0.50)  - start) / range
        x3    = x + w*(data.quantile(0.75)  - start) / range
        x4    = x + w*(data.max             - start) / range
        return cls.boxplot_template.generate(**locals())

    xyscatter_template = template.Template('<circle cx="{{"%0.2f" % cx}}" cy="{{"%0.2f" % cy}}" r="{{rs}}" {{ cls.show_attrs(attr) }}/>')

    @classmethod
    def xyscatter(cls, x, y, w, h, a, b, attr={}, params={}):
        points = min(a.len, b.len)
        r = max(1.0, min(w, h) / points)
        rs = '%0.2f' % r if r > 1.0 else '1'
        x += r
        y += r
        w -= r + r
        h -= r + r
        s = []
        for i in xrange(points):
            v1, v2 = a.value[i], b.value[i]
            if type(v1) == float and type(v2) == float:
                cx = x + w*(v1 - a.min)/a.range
                cy = y + h*(b.max - v2)/b.range
                s.append(cls.xyscatter_template.generate(**locals()))
        return ''.join(s)

    @classmethod
    def split_boxes(cls, rect, data, gap=0, dir='horizontal'):
        '''
        Splits a box into a series of boxes proportional to data.
        The sub-boxes can be horizontal or vertical.
        '''
        rect = [float(v) for v in rect]
        total = float(sum(data) or 1)
        l = sum(1 for val in data if val > 0)
        rects = []
        if dir.startswith('h') or dir.startswith('x'):
            counter = rect[0]
            for value in data:
                d = (rect[2] - gap*l) * value / total
                rects.append((counter, rect[1], d, rect[3]))
                if value > 0: counter += d + gap
        else:
            counter = rect[1]
            for value in data:
                d = (rect[3] - gap*l) * value / total
                rects.append((rect[0], counter, rect[2], d))
                if value > 0: counter += d + gap
        return rects

if __name__ == '__main__':
    import os
    import os.path
    import sys
    import csv

    if len(sys.argv) < 2:
        print __doc__.strip()
        sys.exit(0)

    args = sys.argv[1:]

    # Load multiple data files into source[]
    source = []
    data = []
    while len(args) and os.path.exists(args[0]) and os.path.splitext(args[0])[1].lower() == '.csv':
        filename = args.pop(0)
        data = list(csv.DictReader(open(filename)))
        source.append(data)

    # Load template into tmplfile
    tmplfile = 'template.html'
    if len(args) and os.path.exists(args[0]):
        tmplfile = args.pop(0)

    loader = template.Loader(os.getcwd())
    print loader.load(tmplfile).generate(**globals())
