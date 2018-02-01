#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""Test different hollow Matplotlib markers for scatter plots.

Imitate Gnuplot a bit.
"""

#import matplotlib
#matplotlib.use("module://backend_pgf")

import numpy as np
import matplotlib.pyplot as plt

x = np.random.rand(200)
y = np.random.rand(200)

# not recommended in the same plot: squares and circles.

##-----------------------------------------------------------------------
## using plot():
#plt.plot(x, y, ls="", marker="x", markersize=5.5, markeredgewidth=0.75, markeredgecolor="black", markerfacecolor="None", label="Crosses")
#plt.plot(x[0:100], y[0:100], ls="", marker="+", markersize=5.5, markeredgewidth=0.75, markeredgecolor="black", markerfacecolor="None", label="Plusses")
#plt.plot(x[50:150], y[50:150], ls="", marker="s", markersize=6.5, markeredgewidth=0.75, markeredgecolor="black", markerfacecolor="None", label="Squares")
##plt.plot(x, y, ls="", marker="o", markersize=6.5, markeredgewidth=0.75, markeredgecolor="black", markerfacecolor="None", label="Circles")
#plt.legend(numpoints=1)
#plt.xlabel("$x$")
#plt.ylabel("$y$")
#plt.tight_layout()

#plt.show()

##plt.savefig("testMarker.pdf", dpi=100)  # the dpi setting has to play nicely with the chosen markersizes!

#-----------------------------------------------------------------------
# using scatter:
plt.scatter(x, y, marker="x", color="black", s=30, linewidths=1, label="Crosses")
plt.scatter(x[0:100], y[0:100], marker="+", color="black", s=30, linewidths=1, label="Plusses")
plt.scatter(x[50:150], y[50:150], marker="s", facecolors="None", color="black", s=40, linewidths=1, label="Squares")
#plt.scatter(x[50:150], y[50:150], marker="o", facecolors="None", color="black", s=40, linewidths=1, label="Circles")
plt.xlim((np.min(x), np.max(x)))
plt.ylim((np.min(y), np.max(y)))
plt.legend(scatterpoints=1)
plt.xlabel("$x$")
plt.ylabel("$y$")
plt.tight_layout()

#plt.savefig("testMarker.pdf", dpi=150)  # the dpi setting has to play nicely with the chosen markersizes!

plt.show()
