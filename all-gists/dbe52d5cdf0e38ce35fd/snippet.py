# -*- encoding: UTF-8 -*-

'''
extract all first-level elements (groups and paths) from an SVG file and extract as single SVG files
great to extract multiples glyphes from a single SVG files
works with groups and Line, Rect, Circle, Polyline, Polygon, Path
'''

import os
import re

from xml.etree import ElementTree

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

SVG_NS = "http://www.w3.org/2000/svg"


class Tag(object):
    x_attr = 'x'
    y_attr = 'y'
    def __init__(self, element):
        self.element = element

    def _get_x(self):
        return self.element.attrib.get(self.x_attr)

    def _get_y(self):
        return self.element.attrib.get(self.y_attr)

    @property
    def width(self):
        raise None

    @property
    def height(self):
        raise None

    @property
    def x(self):
        return float(self._get_x())

    @property
    def y(self):
        return float(self._get_y())

    def update(self, min_x, min_y):
        self.element.set(self.x_attr, str(self.x - min_x))
        self.element.set(self.y_attr, str(self.y - min_y))


class Rect(Tag):
    @property
    def width(self):
        return float(self.element.attrib.get('width'))

    @property
    def height(self):
        return float(self.element.attrib.get('height'))


class Circle(Tag):
    x_attr = 'cx'
    y_attr = 'cy'

    def _get_x(self):
        return float(self.element.attrib.get(self.x_attr)) - float(self.element.attrib.get('r'))

    def _get_y(self):
        return float(self.element.attrib.get(self.y_attr)) - float(self.element.attrib.get('r'))

    def update(self, min_x, min_y):
        self.element.set(self.x_attr, str(float(self.element.attrib.get(self.x_attr)) - min_x))
        self.element.set(self.y_attr, str(float(self.element.attrib.get(self.y_attr)) - min_y))

    @property
    def width(self):
        return float(self.element.attrib.get('r')) * 2

    @property
    def height(self):
        return float(self.element.attrib.get('r')) * 2


class Polygon(Tag):

    def _get_points(self):
        return re.split('\s+', self.element.attrib.get('points').strip())

    def _get_x(self):
        min_x = float("inf")
        for coord in self._get_points():
            x, y = coord.split(',')
            min_x = min(min_x, float(x))
        return min_x

    def _get_y(self):
        min_y = float("inf")
        for coord in self._get_points():
            x, y = coord.split(',')
            min_y = min(min_y, float(y))
        return min_y

    def update(self, min_x, min_y):
        new_points = []
        for coord in self._get_points():
            x, y = coord.split(',')
            new_points.append('{0},{1}'.format(
                float(x) - min_x,
                float(y) - min_y
            ))
        self.element.set('points', ' '.join(new_points))

    def _get_size(self):
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        height = 0
        for point in self._get_points():
            x, y = map(lambda a: float(a), point.split(','))
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
        width = max_x - min_x
        height = max_y - min_y
        return width, height

    @property
    def width(self):
        return self._get_size()[0]

    @property
    def height(self):
        return self._get_size()[1]


class Path(Tag):
    REGEXP = 'm(\d+\.\d+,\d+\.\d+)'
    def _get_start(self):
        return re.split(self.REGEXP, self.element.attrib.get('d'))[1]

    def _get_x(self):
        min_x = float("inf")
        start = self._get_start()
        x, y = start.split(',')
        min_x = min(min_x, float(x))
        return min_x

    def _get_y(self):
        min_y = float("inf")
        start = self._get_start()
        x, y = start.split(',')
        min_y = min(min_y, float(y))
        return min_y

    def update(self, min_x, min_y):
        self.element.set('d', re.sub(self.REGEXP,'m{0},{1}'.format(
            float(self.x - min_x),
            float(self.y - min_y)
        ), self.element.attrib.get('d')))

    def get_size(self):
        parts = re.findall(r'(?:[mcls\s]([^mcls\sz]+))', self.element.attrib.get('d'))
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        for part in parts[1:]:
            x, y = part.split(',')
            min_x = min(min_x, float(x))
            max_x = max(max_x, float(x))
            min_y = min(min_y, float(y))
            max_y = max(max_y, float(y))
        width = max_x
        height = max_y
        return width, height

    @property
    def width(self):
        return self.get_size()[0]

    @property
    def height(self):
        return self.get_size()[1]

class Line(Tag):

    def _get_x(self):
        min_x = min(float(self.element.attrib.get('x1')), float(self.element.attrib.get('x2')))
        return min_x

    def _get_y(self):
        min_y = min(float(self.element.attrib.get('y1')), float(self.element.attrib.get('y2')))
        return min_y

    def update(self, min_x, min_y):
        x1 = str(float(self.element.attrib['x1']) - min_x)
        y1 = str(float(self.element.attrib['y1']) - min_y)
        x2 = str(float(self.element.attrib['x2']) - min_x)
        y2 = str(float(self.element.attrib['y2']) - min_y)
        self.element.set('x1', x1)
        self.element.set('x2', x2)
        self.element.set('y1', y1)
        self.element.set('y2', y2)

    @property
    def width(self):
        return float(self.element.attrib.get('x2')) - float(self.element.attrib.get('x1'))

    @property
    def height(self):
        return float(self.element.attrib.get('y2')) - float(self.element.attrib.get('y1'))



class Group(object):
    def __init__(self, element, output_width=350):
        self.element = element
        self.tag_id = element.attrib.get('id')
        self.output_width = output_width
        self.paths = []
        self._init_paths()
        self.update_paths()

    def _init_paths(self):
        '''
        convert group path to local objects
        '''
        self.paths = []
        if self.element.tag.replace('{' + SVG_NS + '}', '') != 'g':
            self.element = [self.element]

        for path in self.element:
            tag = path.tag.replace('{' + SVG_NS + '}', '')
            tag2 = None
            if tag == 'circle':
                tag2 = Circle(path)
            elif tag == 'path':
                tag2 = Path(path)
            elif tag == 'line':
                tag2 = Line(path)
            elif tag == 'rect':
                tag2 = Rect(path)
            elif tag in ['polyline', 'polygon']:
                tag2 = Polygon(path)

            if tag2:
                self.paths.append(tag2)

    def update_paths(self):
        '''
        compute min x, min y, width, height and reposition the paths
        to center the object
        '''
        min_x = float("inf")
        min_y = float("inf")
        width = 0
        height = 0
       # offset_x = offset_y = 50
        for path in self.paths:
            min_x = min(min_x, path.x)
            min_y = min(min_y, path.y)
            width = max(width, path.width)
            height = max(height, path.height)
        offset_x = (self.output_width - width) / 2
        offset_y = (self.output_width - height) / 2
        for path in self.paths:
            path.update(min_x - offset_x, min_y - offset_y)

    def as_svg(self):
        svg = []
        for path in self.paths:
            svg.append(ElementTree.tostring(path.element).replace('ns0:', ''))
        return """<svg width="{0}" height="{0}" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
<g id="{1}">
{2}
</g>
</svg>""".format(
        self.output_width,
        self.tag_id,
        ''.join(svg)
        )

def convertGroup(group):
    tags = []
    if group.tag.replace('{' + SVG_NS + '}', '') != 'g':
        group = [group]

    for path in group:
        tag = path.tag.replace('{' + SVG_NS + '}', '')
        tag2 = None
        if tag == 'circle':
            tag2 = Circle(path)
        elif tag == 'path':
            tag2 = Path(path)
        elif tag == 'line':
            tag2 = Line(path)
        elif tag == 'rect':
            tag2 = Rect(path)
        elif tag in ['polyline', 'polygon']:
            tag2 = Polygon(path)

        if tag2:
            tags.append(tag2)

    return Group(tags)

if __name__=='__main__':

    source = os.path.join(ROOT_PATH, 'GLYPHES-3.svg')

    svg = ElementTree.parse(source)

    svg = svg.getroot()

    # extract all first level elements
    for element in svg.findall('./*'):
        if 'id' in element.attrib and element.attrib.get('id').startswith('svg_'):
            # convert to svg and write iter(collection)
            transformer = Group(element)
            filename = '{0}.svg'.format(element.attrib.get('id'))
            outfile = os.path.join(ROOT_PATH, filename)
            with open(outfile, 'w') as f:
                f.write(transformer.as_svg())
                print '[+] extracted', filename

