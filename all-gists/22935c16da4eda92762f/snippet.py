# coding=utf-8
 
# A simple demonstration of how to load a QGIS project and then
# show it in a widget.
# This code is public domain, use if for any purpose you see fit.
# Tim Sutton 2015
 
import os
from qgis.core import QgsProject
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from qgis.core.contextmanagers import qgisapp
from PyQt4.QtCore import QFileInfo
 
with qgisapp():
    project_path = os.path.dirname(__file__) + os.path.sep + 'test.qgs'
    canvas = QgsMapCanvas(None)  # will reparent it to widget via layout

    # Load our project
    bridge = QgsLayerTreeMapCanvasBridge(
        QgsProject.instance().layerTreeRoot(), canvas)
    QgsProject.instance().read(QFileInfo(project_path))

    canvas.show()