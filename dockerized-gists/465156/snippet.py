from math import sqrt

from matplotlib import pyplot
from shapely.geometry import *

GM = (sqrt(5)-1.0)/2.0
W = 8.0
H = W*GM
SIZE = (W, H)
COLORS = ['#6699cc', '#ffcc33']

def cut(line, distance):
    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i+1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]

def plot_coords(ax, ob):
    # Plot a line's coordinates
    x, y = ob.xy
    ax.plot(x, y, 'o', color='#999999', zorder=1)

def plot_bounds(ax, ob):
    # Plot a line's boundary
    x, y = zip(*list((p.x, p.y) for p in ob.boundary))
    ax.plot(x, y, 'o', color='#000000', zorder=1)

def plot_line(ax, ob, color='#999999'):
    # Plot a line
    x, y = ob.xy
    ax.plot(x, y, color=color, alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)

def arrange(axes):
    # Set axes parameters
    xrange = [-1, 4]
    yrange = [-1, 3]
    axes.set_xlim(*xrange)
    axes.set_ylim(*yrange)
    axes.set_yticks(range(*yrange) + [yrange[-1]])
    axes.set_aspect(1)

# The figure
fig = pyplot.figure(1, figsize=SIZE, dpi=90)

# A simple (non-crossing) line
line = LineString([(0, 0), (1, 1), (0, 2), (2, 2), (3, 1), (1, 0)])

# 1: plot the line
ax = fig.add_subplot(121)
plot_coords(ax, line)
plot_bounds(ax, line)
plot_line(ax, line)
arrange(ax)
ax.set_title('a) Before')


# 2: cut the line and plot the pieces
ax = fig.add_subplot(122)
for piece, color in zip(cut(line, line.length/2.0), COLORS):
    plot_coords(ax, piece)
    plot_bounds(ax, piece)
    plot_line(ax, piece, color=color)
arrange(ax)
ax.set_title('b) After')

pyplot.show()
# pyplot.savefig('cut.png')
