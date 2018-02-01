#!/usr/bin/env python
"""A quick hack to draw gradient lines using a colormap.

This was written in response to <Baribal>'s question on IRC.

There are two functions provided here:

`plot_gradient_hack` takes two arguments, p0 and p1, which are both (x,y)
pairs, and plots a gradient between them that spans the full colormap.

`plot_gradient_rbg_pairs` does the same thing, but also takes rgb0 and rgb1
arguments, makes a new colormap that spans between those two values, and uses
that colormap for the plot.

There's an alternative solution over here [1], but that uses many more points.

1.  http://matplotlib.1069221.n5.nabble.com/Gradient-color-on-a-line-plot-td17643.html
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import LinearSegmentedColormap

def plot_gradient_hack( p0, p1, npts=20, cmap=None, **kw):
    """
    Draw a gradient between p0 and p1 using a colormap

    The **kw dictionary gets passed to plt.plot, so things like linestyle,
    linewidth, labels, etc can be modified directly.
    """
    x_1, y_1 = p0
    x_2, y_2 = p1
    
    X = np.linspace(x_1, x_2, npts)
    Xs = X[:-1]
    Xf = X[1:]
    Xpairs = zip(Xs, Xf)
    
    Y = np.linspace(y_1, y_2, npts)
    Ys = Y[:-1]
    Yf = Y[1:]
    Ypairs = zip(Ys, Yf)

    C = np.linspace(0,1, npts)
    cmap = plt.get_cmap(cmap)
    # the simplest way of doing this is to just do the following:
    for x, y, c in zip(Xpairs, Ypairs, C):
        plt.plot(x, y, '-', c=cmap(c), **kw)

    # But for cases when that  will be too slow, you can make this go faster,
    # follow along with this example:
    # http://matplotlib.org/examples/pylab_examples/line_collection2.html


def plot_gradient_rbg_pairs(p0, p1, rgb0, rgb1, **kw):
    """Form the gradient from RGB values at each point


    The **kw dictionary gets passed to plt.plot, so things like linestyle,
    linewidth, labels, etc can be modified directly.
    """
    cmap = LinearSegmentedColormap.from_list('tmp', (rgb0, rgb1))
    plot_gradient_hack(p0, p1, cmap=cmap, **kw)

# plot gradient that just spans the full colormap
plot_gradient_hack( (1,2), (5,6) )

# we can specify the colormap, and set some properties for the plot
plot_gradient_hack( (2,5), (5,3), cmap='bwr', linewidth=3.)

# We also have a simple wrapper to specify the two rgb points to interpolate
# the gradient between
plot_gradient_rbg_pairs( (1.1,2), (5.1,6), (0,0,0), (1,1,1) ) # black to white
plot_gradient_rbg_pairs( (1.2,2), (5.2,6), (0,0,0), (0,0,1),  # black to blue
                         linestyle='--', linewidth=9) 
plot_gradient_rbg_pairs( (1.3,2), (5.3,6), (1,0,0), (0,1,0),  # red to green
                         linewidth=4 )

plt.show()

# we can use this gradient plot to display all colormaps on one plot easily
plt.figure()
with matplotlib.rc_context({'lines.solid_capstyle':'butt'}):
    # the default projecting capstyle looks kind of ugly. rc_context was
    # introduced in matpltolib 1.2.0, if you are running a version older than
    # that, you can ignore this line and remove one level of indentation from
    # the for loop
    for i, map_name in enumerate(plt.cm.cmap_d):
        plot_gradient_hack((0, i), (1, i), cmap = map_name, linewidth=4)
        plt.text(1,i, map_name, va='center')
        # comment out this last line to plot all ~140 colormaps
        if i==25: break
plt.show()
