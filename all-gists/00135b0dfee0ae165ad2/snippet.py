from PyQt4 import QtGui, QtCore
import maya.OpenMayaUI as mui
import sip

DOCK_OBJECT = "dock_name"
DEFAULT_DOCK = QtCore.Qt.RightDockWidgetArea

# Get Main Window
pointer = mui.MQtUtil.mainWindow()
maya_main_window = sip.wrapinstance(long(pointer), QtCore.QObject)

# Check for existing dock
existing_dock = maya_main_window.findChild(QtGui.QDockWidget, DOCK_OBJECT)
if existing_dock:
    existing_dock.deleteLater()

# Create Your New DockWidget Instance here
dock_instance = MyDockInstance()

# Add to Dock
# If Existing DockWdiget found on default DockArea then Dock is Tabified otherwise added as first DockWidget
docked = False
for dock_widget in maya_main_window.findChildren(QtGui.QDockWidget):
    if maya_main_window.dockWidgetArea(dock_widget) == DEFAULT_DOCK:
        maya_main_window.tabifyDockWidget(dock_widget, dock_instance)
        docked = True
        break

if not docked:
    maya_main_window.addDockWidget(DEFAULT_DOCK, dock_instance)