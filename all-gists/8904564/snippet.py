"""
Utility functions for hex grids.
"""

from math import sqrt
from heapq import heappush, heappop
import numpy
import numpy.random

neighbours = numpy.array(((2, 0), (1, 1), (-1, 1), (-2, 0), (-1, -1), (1, -1)))

def _tiled_range(lo, hi, tile_size):
    return (lo // tile_size, (hi + tile_size - 1) // tile_size) 

def _make_range(x, width, bloat, grid_size):
    return _tiled_range(x + grid_size - 1 - bloat, x + width + bloat, grid_size)

def distance(pos):
    """Distance of (x, y) from the origin on the hex grid,
    i.e. the number of setps which are needed to reach (x, y) from (0, 0).
    """
    pos = numpy.abs(pos)
    x = pos[...,0]
    y = pos[...,1]
    return y + numpy.maximum(0, (x - y) // 2)

_point_type = [("x", numpy.int), ("y", numpy.int)]

def make_index_array(ar):
    ar = numpy.ascontiguousarray(ar).view(dtype=_point_type)
    shape = ar.shape[:-1]
    ar, inv = numpy.unique(ar, return_inverse=True)
    return (ar.view(numpy.int).reshape((-1, 2)), inv.reshape(shape))

class HexGrid:
    """Represents the dimensions of a hex grid as painted on the screen.
    The hex grid is assumed to be aligned horizontally, like so:
       / \ / \ / \ 
      |   |   |   |
       \ / \ / \ /
    The center of hex (0, 0) is assumed to be on pixel (0, 0).
    The hexgrid is determined by width and height, which are the screen coordinates
    of the upper-right corner of the central hex.

    To have equilateral hexes, width:height should be √3 : 1.
    If you only pass in width to the constructor, the height is computed to be
    an integer as close as possible to width / √3 .
    """
       
    _factor = sqrt(1.0/3.0)
    _corners = numpy.array(((1, 1), (0, 2), (-1, 1), (-1, -1), (0, -2), (1, -1)))

    def __init__(self, width, height=None):
        if height is None:
            height = round(width * self._factor)
        self.width = width
        self.height = height
        self.size = numpy.array((width, height))
        self.polygon = self._corners * self.size

        self.center_at = numpy.array((width, 3 * height)).__mul__

    def __repr__(self):
        return "HexGrid(%d, %d)" % (self.width, self.height)

    def hexes_in_rectangle(self, x, y, width, height):
        x_lo, x_hi = _make_range(x, width, self.width, self.width)
        y_lo, y_hi = _make_range(y, height, 2*self.height, 3*self.height)
        xs = numpy.arange(x_lo, x_hi, dtype=numpy.uint8)[:,numpy.newaxis]
        ys = ~numpy.arange(y_lo, y_hi, dtype=numpy.uint8)[numpy.newaxis,:]
        numpy.bitwise_and(xs, 1, xs)
        numpy.bitwise_and(ys, 1, ys)
        sum = numpy.bitwise_xor(xs, ys)
        return numpy.transpose(numpy.nonzero(sum)) + (x_lo, y_lo)

    def center_at(self, pos):
        return (self.width * x, 3 * self.height * y)

    def polygon_at(self, pos):
        return self.center_at(pos)[..., numpy.newaxis,:] + self.polygon

    def cairo_surface(self):
        import cairo
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 2*self.width, 6*self.height)
        cr = cairo.Context(surface)
        for poly in self.polygon_at(self.hexes_in_rectangle(0, 0, surface.get_width(), surface.get_height())):
            cr.move_to(*poly[0])
            for point in poly[1:]:
                cr.line_to(*point)
            cr.close_path()
        cr.stroke()
        return surface

    def hex_at_coordinate(self, x, y):
        width = self.width
        height = self.height
        x0 = x // width
        δx = x % width
        y0 = y // (3 * height)
        δy = y % (3 * height)

        if (x0 + y0) % 2 == 0:
            if width * δy < height * (2 * width - δx):
                return (x0, y0)
            else:
                return (x0 + 1, y0 + 1)
        elif width * δy < height * (width + δx):
            return (x0 + 1, y0)
        else:
            return (x0, y0 + 1)



class HexPathFinder:
    """A* path-finding on the hex grid.
    All positions are represented as tuples of (x, y) - coordinates.

    Important data attributes: 
    found -- True if path-finding is complete and we found a path
    done  -- True if path-finding is complete: we either found a path or know there isn't one
    path  -- The path, as a tuple of positions from start to destination (including both). Empty tuple if found is False.
    """

    found = False
    done = False
    path = ()
    
    def __init__(self, start, destination, passable, cost=lambda pos: 1):
        """Create a new HexPathFinder object.
        start       -- Starting position for path finding.
        destination -- Destination position for path finding.
        passable    -- Function of one position, returning True if we can move through this hex.
        cost        -- cost function for moving through a hex. Should return a value ≥ 1. By default all costs are 1.
        """
        self.start = start
        self.destination = destination
        self.passable = passable
        self.cost = cost
        self.closedset = set()
        self.openset = [(self._heuristic(start), 0, start, ())]

    def _heuristic(self, position):
        return distance(numpy.asarray(position) - self.destination)

    def _compute_path(self, path):
        result = []
        while path:
            pos, path = path
            result.append(pos)
        return result[::-1]

    def run_n(self, n):
        """Run at most n path-finding steps.
        This method does a bounded amount of work, and is therefore useful
        if pathfinding must be interleaved with interactive behaviour or may
        be interrupted.
         """
        openset = self.openset
        closedset = self.closedset
        passable = self.passable
        cost = self.cost
        destination = self.destination
        heuristic = self._heuristic

        for i in range(n):
            if not openset:
                self.done = True
                return
            h, cur_cost, pos, path = heappop(openset)
            if pos in closedset:
                continue
            new_path = (pos, path)
            if pos == destination:
                self.path = self._compute_path(new_path)
                self.found = self.done = True
                del openset[:]
                return
            closedset.add(pos)
            for new_pos in neighbours + pos:
                new_pos = tuple(new_pos)
                if (not passable(new_pos)) or (new_pos in closedset):
                    continue
                new_cost = cur_cost + cost(new_pos)
                new_h = new_cost + heuristic(new_pos)
                heappush(openset, (new_h, new_cost, new_pos, new_path))

    def run(self):
        """Run path-finding until done, that is, we either found a path or know there isn't one.
        """
        while not self.done:
            self.run_n(100)


def rotate_left(x, y):
    """Given a hex coordinate (x, y) return the coordinate of hex when rotated 60° around the origin.
    """
    return ((x - 3 * y) >> 1, (x + y) >> 1)

class _FovTree:
    _corners = ((0, -2), (1, -1), (1, 1), (0, 2))
    _neighbours = ((1, -1), (2, 0), (1, 1))
    _cached_successors = None

    def __init__(self, x, y, angle1, angle2):
        self.x = x
        self.y = y
        self.angle1 = angle1
        self.angle2 = angle2
        self.distance = 0.5 * sqrt(x*x + 3*y*y)
        self.points = self.make_points()

    def run(self, transparent, visible, direction, x0, y0, max_distance):
        if self.distance <= max_distance:
            δx, δy = self.points[direction]
            point = (x0 + δx, y0 + δy)
            visible.add(point)
            if transparent(point):
                for successor in self.successors():
                    successor.run(transparent, visible, direction, x0, y0, max_distance)

    def make_points(self):
        x = self.x
        y = self.y
        result = []
        for i in range(6):
            result.append((x, y))
            x, y = rotate_left(x, y)
        return tuple(result)

    def get_angle(self, corner):
        cx, cy = corner
        return (3*self.y + cy)/float(self.x + cx)

    def successors(self):
        _cached_successors = self._cached_successors
        if _cached_successors is None:
            _cached_successors = []
            angles = [self.get_angle(c) for c in self._corners]
            for i in range(3):
                c1 = max(self.angle1, angles[i])
                c2 = min(self.angle2, angles[i+1])
                if c1 < c2:
                    dx, dy = self._neighbours[i]
                    _cached_successors.append(_FovTree(self.x + dx, self.y + dy, c1, c2))
            self._cached_successors = _cached_successors = tuple(_cached_successors)

        return _cached_successors

_fovtree = _FovTree(2, 0, -1.0, 1.0)

def run_fov(transparent, max_distance, origin=(0, 0), visible=None):
    """Compute field-of-view on the hex grid.
     transparent  -- function accepting a (x, y)-tuple and returning True is the hex is transparent (open)
     max_distance -- maximum distance that we can see
     origin       -- (x, y)-tuple indicating the location of the viewer
     visible      -- a set of (x,y)-tuples which will be updated with the visible locations and returned

    This function returns a set of (x,y)-tuples which are visible.
    Not that the origin is always added, even if transparent woudl return False for it.
    By passing in an existing set as "visible", multiple viewers can re-use the same set.
    """

    if visible is None:
        visible = set()
    visible.add(origin)
    x0, y0 = origin
    for direction in range(6):
        _fovtree.run(transparent, visible, direction, x0, y0, max_distance)
    return visible


def random_walk(N, origin=(0, 0)):
    """Return a set of (x,y)-tuples representing a random walk starting from origin."""

    result = numpy.add.accumulate(neighbours[numpy.random.randint(0, 6, N)])
    result += origin
    result = set(map(tuple, result))
    result.add(origin)

    return result
