import maya.OpenMayaUI
import maya.cmds as cmds
import sip
from PyQt4.QtGui import *
from PyQt4.QtCore import *

mainWindow = QMainWindow()
centralWidget = QListView()
mainWindow.setCentralWidget(centralWidget)
dockWidget = QDockWidget("DockWidget", mainWindow)
dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

mayaMainWindow = sip.wrapinstance(long(maya.OpenMayaUI.MQtUtil.mainWindow()), QObject)
channelBoxDockWidget = None

widget = cmds.attrColorSliderGrp("__MyWidget__")

dockWidget.setWidget([widget for widget in mayaMainWindow.findChildren(QWidget, "__MyWidget__")][0])

mainWindow.addDockWidget(Qt.DockWidgetArea(Qt.LeftDockWidgetArea), dockWidget)
mainWindow.show()