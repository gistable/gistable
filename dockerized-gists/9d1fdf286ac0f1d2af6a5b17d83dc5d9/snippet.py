"""
Examples:

with figure_grid(5, 3) as grid:
  grid.next()
  # plot something
  grid.next()
  # plot something
  # ...etc
  
with figure_grid(10, 4) as grid:
  for i, axis in enumerate(grid.each_subplot()):
    # plot something
"""

import matplotlib.pyplot as plt

class figure_grid():
    def next_subplot(self, **kwargs):
        if self.subplots:
          self.after_each()
        self.subplots += 1
        return self.fig.add_subplot(self.rows, self.cols, self.subplots, **kwargs)

    def each_subplot(self):
        for _ in range(self.rows * self.cols):
            yield self.next_subplot()

    def title(self, title, fontsize=14, **kwargs):
        self.fig.suptitle(title, y=1.05, fontsize=fontsize, **kwargs)

    def __init__(self, rows, cols, rowheight=3, rowwidth=12, after_each=lambda: None):
        self.rows = rows
        self.cols = cols
        self.fig = plt.figure(figsize=(rowwidth, rowheight*self.rows))
        self.subplots = 0
        if after_each == 'legend':
          after_each = lambda: plt.legend(loc='best')
        self.after_each = after_each

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        self.after_each()
        plt.tight_layout()
        plt.show()

    next = next_subplot