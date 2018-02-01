# vim: set expandtab ts=4 sw=4 filetype=python:

import unittest

class Cell(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def neighbors(self):
        return [
            Cell(self.x-1, self.y+1),
            Cell(self.x, self.y+1),
            Cell(self.x+1, self.y+1),
            Cell(self.x+1, self.y),
            Cell(self.x+1, self.y-1),
            Cell(self.x, self.y-1),
            Cell(self.x-1, self.y-1),
            Cell(self.x-1, self.y),
        ]

    def __eq__(self, otherguy):

        return self.x == otherguy.x and self.y == otherguy.y

    def __str__(self):
        return "Cell(%s, %s)" % (self.x, self.y)


class Grid(object):

    def __init__(self, cells):
        self.cells = cells

    def generate_next_grid(self):

        g = Grid([])

        for cell in self.cells:

            for neighbor in cell.neighbors():

                living_neighbors = 0

                if neighbor in self.cells:
                    i_am_alive = True

                else:
                    i_am_alive = False

                for non in neighbor.neighbors():

                    if non in self.cells:
                        living_neighbors += 1

                if i_am_alive and living_neighbors in (2, 3):
                    g.cells.append(neighbor)

                if not i_am_alive and living_neighbors == 3:
                    g.cells.append(neighbor)

        return g

    def __str__(self):

        s = ''

        for row in xrange(11):

            for col in xrange(11):

                if Cell(col, row) in self.cells:
                    s += 'x'

                else:
                    s += '.'

            s += '\n'

        return s



class TestGetMyNeighbors(unittest.TestCase):

    def test_1(self):

        cell = Cell(4, 9)

        neighbors = cell.neighbors()

        assert len(set(neighbors)) == 8, \
        'got %s elements back!' % len(set(neighbors))


class TestBlinker(unittest.TestCase):

    def setUp(self):

        self.cells = [
            Cell(4, 8), Cell(5, 8), Cell(6, 8)]

        self.grid = Grid(self.cells)

    def test_generate_next_grid(self):

        next_grid = self.grid.generate_next_grid()

        assert Cell(5, 7) in next_grid.cells, \
        'next_grid.cells is %s' % next_grid.cells

        assert Cell(5, 8) in next_grid.cells
        assert Cell(5, 9) in next_grid.cells

if __name__ == '__main__':
    unittest.main()
