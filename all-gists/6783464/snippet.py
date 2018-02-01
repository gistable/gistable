import csv

class Grid(object):
    '''Parses a csv file into a grid. Each cell in the grid is a list of strings, corresponding to
    the string that was in the corresponding cell in the spreadsheet split by the given
    'cell_item_separator', which defaults to a comma'''
    def __init__(self, csv_text, width=0, height=0, cell_item_separator=','):
        lines = list(csv.reader(csv_text.splitlines()))

        self.height = height if height > 0 else len(lines)
        if self.height <= 0:
            raise Exception("height must be > 0 [height=%d]" % self.height)

        # each cell is a list of 0 or more strings, separated by our cell_item_separator
        self.rows = []
        for line in lines:
            row = []
            # split the row into comma-separated cells;
            # split each cell into |-separated strings;
            # strip whitespace from each string;
            # drop empty cells
            for cell in [cell.split(cell_item_separator) for cell in line]:
                row.append([cell_text.strip() for cell_text in cell if len(cell_text.strip()) > 0])
            self.rows.append(row)

        self.width = width if width > 0 else max([len(row) for row in self.rows])
        if self.width <= 0:
            raise Exception("width must be > 0 [width=%d]" % self.width)

        # make all rows the same length
        for ii in xrange(len(self.rows)):
            row = self.rows[ii]
            # trim
            if len(row) > self.width:
                self.rows[ii] = row[:self.width]
            # extend
            while len(row) < self.width:
                row.append([])

    @property
    def cells(self):
        '''a generator that returns tuples in the form (x, y, cell) for each cell in the grid'''
        for y in xrange(self.height):
            for x in xrange(self.width):
                yield (x, y, self.rows[y][x])

    @property
    def symbols(self):
        '''a generator that returns tuples in the form (x, y, symbol) for each symbol in the grid
        (each cell contains a list of 0 or more symbols, so this will only yield results for
        non-empty cells)'''
        for (x, y, cell) in self.cells:
            for symbol in cell:
                yield (x, y, symbol)

    def get_cell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise Exception("bad coordinate")
        return self.rows[y][x]