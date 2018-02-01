import cv2
import json
import numpy
import re
import sys

from operator import itemgetter, attrgetter
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

NUMBER_OF_LINES = 68
DOT_COLOR = "FFFFFF"
ALL_COLORS = [
    ("ff0000", "red"),
    ("00ff00", "green"),
    ("c7caeb", "violet"),
    ("01b6af", "lightblue"),
    ("fe8407", "orange"),
    ("ffd064", "orange"),
    ("0493cd", "blue"),
    ("4BBBFF", "blue"),
    ("e7236f", "pink"),
    ("f0fd3b", "yellow"),
    ("9dc9c8", "lightgreen"),
]


class Color(object):

    def __init__(self, red, green, blue, name=None):
        self.components = (blue, green, red)
        self.name = name
        self._srgb = sRGBColor(red, green, blue, is_upscaled=True)

    @property
    def hex(self):
        b, g, r = self. components
        return "#%.6x" % (r << 16 | g << 8 | b)

    @property
    def closest(self):
        if getattr(Color, '_colors', None) is None:
            Color._colors = map(lambda x: Color.from_hex(*x), ALL_COLORS)

        return min((self.distance(color), color) for color in Color._colors)

    @classmethod
    def from_hex(self, hexstring, name=None):
        rgb = [int(hexstring[i * 2:i * 2 + 2], 16) for i in xrange(3)]
        return Color(*rgb, name=name)

    def distance(self, color):
        return delta_e_cie2000(convert_color(self._srgb, LabColor),
                               convert_color(color._srgb, LabColor))


class Contour(object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bottom = y + height
        self.right = x + width

    @property
    def is_valid(self):
        return self.width > 13 and self.height > 13

    def is_dot_in(self, image):
        dot_color = Color.from_hex(DOT_COLOR)
        is_small = self.width < 25 and self.height < 25
        is_square = abs(float(self.width) / self.height - 1.0) < 0.2

        return is_small and is_square and \
            self.median_color(image).distance(dot_color) < 11

    def median_color(self, image):
        piece = image.cvimage[self.y:self.bottom, self.x:self.right]
        piece = piece.reshape(numpy.prod(piece.shape[:2]), -1)
        colors = piece[~numpy.all(piece == 0, axis=1)]

        return Color(*numpy.median(colors, axis=0)[::-1])

    def draw_into(self, image, color, stroke=2, offset=0):
        cv2.rectangle(image.cvimage, (self.x - offset, self.y - offset),
                      (self.right + offset, self.bottom + offset),
                      color.components, stroke)

    def merge(self, contour):
        right = max(self.right, contour.right)
        bottom = max(self.bottom, contour.bottom)

        x = min(self.x, contour.x)
        y = min(self.y, contour.y)
        return Contour(x, y, right - x, bottom - y)


class Image(object):

    def __init__(self, path, size=None):
        self.cvimage = cv2.imread(path)

        if size is not None:
            self.cvimage = cv2.resize(self.cvimage, size)

        self.height, self.width = self.cvimage.shape[:2]

    def mask(self, black_and_white_image):
        self.cvimage = cv2.bitwise_and(self.cvimage, self.cvimage,
                                       mask=black_and_white_image.cvimage)

    def save(self, path):
        cv2.imwrite(path, self.cvimage)


class BlackAndWhiteImage(Image):

    def __init__(self, path):
        super(BlackAndWhiteImage, self).__init__(path)
        gray = cv2.cvtColor(self.cvimage, cv2.COLOR_BGR2GRAY)
        _, self.cvimage = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    def contours(self):
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2))
        dilated = cv2.dilate(self.cvimage, kernel, iterations=5)

        _, contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)
        return filter(
            lambda x: x.is_valid,
            map(lambda c: Contour(*cv2.boundingRect(c)), contours)
        )

    def contours_by_line(self, lines=NUMBER_OF_LINES):
        """
        Arrange contours into groups where elements are "in line" to the
        first contours (initial "Hello" on the line).
        """
        contours = self.contours()
        contours.sort(key=attrgetter('x'))

        left_contours = sorted(contours[:lines], key=attrgetter('bottom'))
        left_ys = numpy.array(map(attrgetter('bottom'), left_contours))

        groups = map(lambda x: [x], left_contours)
        for contour in contours[lines:]:
            distance_matrix = numpy.abs(left_ys - contour.bottom)
            nearest = distance_matrix.argmin()

            # Make sure the contour belong here.
            if groups[nearest][-1].bottom > contour.y:
                groups[nearest].append(contour)

        return groups


class HelloText(object):

    def __init__(self, text):
        self.lines = text.split("\n")

    def sentences(self, line):
        groups = re.finditer("[!?.\"] H", self.lines[line])
        sentences = re.split("[!?.\"] H", self.lines[line])

        groups = [g.group()[0] for g in groups] + [""]
        for i, sentence in enumerate(sentences):
            prefix = "H" if i > 0 else ""
            yield prefix + sentence + groups[i]


def cluster_colors(contours, color_image):
    last_contour = contours[0]
    last_color = contours[0].median_color(color_image)
    for contour in contours[1:]:
        median_color = contour.median_color(color_image)
        color_is_close = last_color.distance(median_color) < 18
        if not contour.is_dot_in(color_image) and color_is_close:
            last_contour = last_contour.merge(contour)
        else:
            yield last_contour
            last_contour = contour

        last_color = median_color

    yield last_contour


def main():
    if len(sys.argv) < 5:
        print "Usage: %s <color file> <bw file> <text file> <json file>" % \
            sys.argv[0]

        sys.exit(1)

    text = HelloText(open(sys.argv[3]).read())
    bw_image = BlackAndWhiteImage(sys.argv[2])
    color_image = Image(sys.argv[1], size=(bw_image.width, bw_image.height))

    # Black-out the areas that are not letters
    color_image.mask(bw_image)

    lines = []
    for i, line in enumerate(bw_image.contours_by_line()):
        sentences = text.sentences(i)
        clusters = filter(lambda x: x.width > 200,
                          cluster_colors(line, color_image))

        line = []
        for contour in clusters:
            median_color = contour.median_color(color_image)
            distance, color = median_color.closest
            line.append({
                "sentence": sentences.next(),
                "color": color.name
            })

        lines.append(line)

    open(sys.argv[4], "w").write(json.dumps(lines))


if __name__ == "__main__":
    main()
