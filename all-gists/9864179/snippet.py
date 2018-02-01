from math import sqrt
from heapq import heappush, heappop, nsmallest


class Point:
    def __init__(self, coord, data=None):
        self.coord = coord
        self.data = data
        self.dest = None

    def __lt__(self, other):
        return self.distance() < other.distance()
    
    def __gt__(self, other):
        return self.distance() > other.distance()

    def distance(self, other=None):
        other = other or self.dest
        return sqrt(sum(map(lambda coord: (coord[0] - coord[1]) * (coord[0] - coord[1]), zip(self.coord, other.coord))))


class KDTree:
    def __init__(self, d=3):
        self.current_i = 0
        self.d = d
        self.root = {}

    def index(self):
        return self.current_i % self.d

    def insert(self, coord, value):
        self.current_i = 0
        self._insert(self.root, coord, value)

    def _insert(self, node, coord, value):
        if not node:
            node['point'], node['left'], node['right'] = Point(coord, value), {}, {}
            return
        if coord[self.index()] > node['point'].coord[self.index()]:
            self.current_i += 1
            self._insert(node['right'], coord, value)
        else:
            self.current_i += 1
            self._insert(node['left'], coord, value)

    def nearest(self, coord, k=1):
        self.pq = []
        self.current_i = 0
        self._nearest(self.root, coord)
        return nsmallest(k, self.pq)

    def _nearest(self, node, coord):
        if not node: return
        node['point'].dest = Point(coord)
        heappush(self.pq, node['point'])
        if coord[self.index()] < node['point'].coord[self.index()]:
            self.current_i += 1
            self._nearest(node['left'], coord)
            if coord[self.index()] + self.pq[-1].distance() > node['point'].distance():
                self.current_i += 1
                self._nearest(node['right'], coord)
        else:
            self.current_i += 1
            self._nearest(node['right'], coord)
            heappush(self.pq, node['point'])
            if coord[self.index()] + self.pq[-1].distance() > node['point'].distance():
                self.current_i += 1
                self._nearest(node['left'], coord)

class Classifier:

    def __init__(self, training_file):
        self.training_file = training_file
        self.tree = KDTree(4)
        self.index_content()

    def index_content(self):
        content = open(self.training_file)
        content.readline()
        parsed_data = self._parsed_data(content)
        median = parsed_data.pop(len(parsed_data)/2)
        self.tree.insert(median['measures'], median['type'])
        for data in parsed_data:
            self.tree.insert(data['measures'], data['type'])

    def classify(self, dataset, k):
        result = []
        file = open(dataset)
        file.readline()
        for data in self._parsed_input(file): 
            types = {'0': 0, '1': 0, '2': 0}
            for point in self.tree.nearest(data, k):
                types[point.data] += 1
            result.append(str(max(types, key=types.get)))
        self.check_result(result, k)

    def check_result(self, results, k):
        expected = map(lambda s: s.strip(), open('rotulos-teste.txt').xreadlines())
        count = 0
        for result in zip(results, expected):
            if result[0] == result[1]:
                count +=1
        print '%d/%d - %.1f%% de acerto com k=%d' %(count, len(results), count * 100/len(results), k)

    def _parsed_input(self, content):
        for line in content.xreadlines():
            yield map(float, line.strip().split(','))

    def _parsed_data(self, content):
        data = []
        for line in content.xreadlines():
            values = line.strip().split(',')
            data.append({'measures': tuple(map(float, values[:4])), 'type': values[-1]})
        return sorted(data, key=lambda d: float(sum(d['measures']))/len(d['measures']))

classifier = Classifier('treinamento.csv')
for k in range(1, 20):
    classifier.classify('teste.csv', k)

