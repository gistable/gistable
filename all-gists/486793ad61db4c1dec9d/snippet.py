# coding=utf-8

# A simple demonstration of to generate a PDF using a QGIS project
# and a QGIS layout template.
#
# This code is public domain, use if for any purpose you see fit.
# Tim Sutton 2015

import sys
from qgis.core import (
    QgsProject, QgsComposition, QgsApplication, QgsProviderRegistry)
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from PyQt4.QtCore import QFileInfo
from PyQt4.QtXml import QDomDocument


gui_flag = True
app = QgsApplication(sys.argv, gui_flag)

# Make sure QGIS_PREFIX_PATH is set in your env if needed!
app.initQgis()

# Probably you want to tweak this
project_path = 'project.qgs'

# and this
template_path = 'template.qpt'

def make_pdf():
    canvas = QgsMapCanvas()
    # Load our project
    QgsProject.instance().read(QFileInfo(project_path))
    bridge = QgsLayerTreeMapCanvasBridge(
        QgsProject.instance().layerTreeRoot(), canvas)
    bridge.setCanvasLayers()

    template_file = file(template_path)
    template_content = template_file.read()
    template_file.close()
    document = QDomDocument()
    document.setContent(template_content)
    composition = QgsComposition(canvas.mapSettings())
    # You can use this to replace any string like this [key]
    # in the template with a new value. e.g. to replace
    # [date] pass a map like this {'date': '1 Jan 2012'}
    substitution_map = {
        'DATE_TIME_START': 'foo',
        'DATE_TIME_END': 'bar'}
    composition.loadFromTemplate(document, substitution_map)
    # You must set the id in the template
    map_item = composition.getComposerItemById('map')
    map_item.setMapCanvas(canvas)
    map_item.zoomToExtent(canvas.extent())
    # You must set the id in the template
    legend_item = composition.getComposerItemById('legend')
    legend_item.updateLegend()
    composition.refreshItems()
    composition.exportAsPDF('report.pdf')
    QgsProject.instance().clear()


make_pdf()
