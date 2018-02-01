import matplotlib

matplotlib.use('webagg')

import numpy as np
from scipy.special import binom

import matplotlib.pyplot as plt

from matplotlib.lines import Line2D


class BezierBuilder(object):
    """Bézier curve interactive builder.

    """
    def __init__(self, control_polygon, ax_bernstein):
        """Constructor.

        Receives the initial control polygon of the curve.

        """
        self.control_polygon = control_polygon
        self.xp = list(control_polygon.get_xdata())
        self.yp = list(control_polygon.get_ydata())
        self.canvas = control_polygon.figure.canvas
        self.ax_main = control_polygon.get_axes()
        self.ax_bernstein = ax_bernstein

        # Event handler for mouse clicking
        self.cid = self.canvas.mpl_connect('button_press_event', self)

        # Create Bézier curve
        line_bezier = Line2D([], [],
                             c=control_polygon.get_markeredgecolor())
        self.bezier_curve = self.ax_main.add_line(line_bezier)

    def __call__(self, event):
        # Ignore clicks outside axes
        if event.inaxes != self.control_polygon.axes:
            return

        # Add point
        self.xp.append(event.xdata)
        self.yp.append(event.ydata)
        self.control_polygon.set_data(self.xp, self.yp)

        # Rebuild Bézier curve and update canvas
        self.bezier_curve.set_data(*self._build_bezier())
        self._update_bernstein()
        self._update_bezier()

    def _build_bezier(self):
        x, y = Bezier(list(zip(self.xp, self.yp))).T
        return x, y

    def _update_bezier(self):
        self.canvas.draw()

    def _update_bernstein(self):
        N = len(self.xp) - 1
        t = np.linspace(0, 1, num=200)
        ax = self.ax_bernstein
        ax.clear()
        for kk in range(N + 1):
            ax.plot(t, Bernstein(N, kk)(t))
        ax.set_title("Bernstein basis, N = {}".format(N))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)


def Bernstein(n, k):
    """Bernstein polynomial.

    """
    coeff = binom(n, k)

    def _bpoly(x):
        return coeff * x ** k * (1 - x) ** (n - k)

    return _bpoly


def Bezier(points, num=200):
    """Build Bézier curve from points.

    """
    N = len(points)
    t = np.linspace(0, 1, num=num)
    curve = np.zeros((num, 2))
    for ii in range(N):
        curve += np.outer(Bernstein(N - 1, ii)(t), points[ii])
    return curve


if __name__ == '__main__':
    # Initial setup
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Empty line
    line = Line2D([], [], ls='--', c='#666666',
                  marker='x', mew=2, mec='#204a87')
    ax1.add_line(line)

    # Canvas limits
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_title("Bézier curve")

    # Bernstein plot
    ax2.set_title("Bernstein basis")

    # Create BezierBuilder
    bezier_builder = BezierBuilder(line, ax2)

    plt.show()
