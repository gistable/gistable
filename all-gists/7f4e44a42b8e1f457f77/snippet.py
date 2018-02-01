#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

## namespace organization changed in PyQt5 but the class name was kept.
## importing this way makes it easier to change to PyQt5 later
from PyQt4.QtGui import (QMainWindow, QApplication, QDockWidget, QWidget,
                         QGridLayout, QSlider)
from PyQt4.QtCore import Qt

import numpy
import matplotlib.pyplot
import matplotlib.backends.backend_qt4agg

class MainWindow (QMainWindow):

  x = numpy.arange (0, 10, 0.1)
  cos = 0
  sin = 0

  def __init__ (self):
    QMainWindow.__init__ (self)

    self.figure  = matplotlib.pyplot.figure ()
    self.drawing = self.figure.add_subplot (111)
    self.canvas  = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg (self.figure)

    self.setCentralWidget (self.canvas)

    dock = QDockWidget ("Values")
    self.addDockWidget (Qt.RightDockWidgetArea, dock)

    sliders = QWidget ()
    sliders_grid = QGridLayout (sliders)

    def add_slider (foo, col):
      sld = QSlider (Qt.Vertical, sliders)
      sld.setFocusPolicy (Qt.NoFocus)
      sld.valueChanged[int].connect (foo)
      sld.valueChanged.connect (self.plot)
      sliders_grid.addWidget (sld, 0, col)

    add_slider (foo = self.set_cos, col = 0)
    add_slider (foo = self.set_sin, col = 1)

    dock.setWidget (sliders)

    self.plot ()

  def set_cos (self, v):
    self.cos = v / float (100)

  def set_sin (self, v):
    self.sin = v / float (100)

  def plot (self):
    self.drawing.hold (False)
    s = numpy.sin (self.x + self.sin)
    c = numpy.cos (self.x + self.cos)
    self.drawing.plot (self.x, s, 'r', self.x, c, 'r', self.x, s +c, 'b')
    self.drawing.set_ylim (-2, 2)
    self.canvas.draw ()

if __name__ == "__main__":
  app = QApplication (sys.argv)
  main = MainWindow ()
  main.show ()
  sys.exit (app.exec_ ())