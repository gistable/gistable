from PyQt4 import QtCore, QtGui
import maya.cmds as cmds
import maya.OpenMayaUI as mui
import sip

def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

widget = QtGui.QDialog(getMayaWindow())
widget.setObjectName("myWidget")

button = QtGui.QPushButton("Right Click (hold) Me", widget)
button.setObjectName("myButton")

layout = QtGui.QVBoxLayout(widget)
layout.setObjectName("myLayout")
layout.addWidget(button)

# Get the Maya path name to the widget
name = mui.MQtUtil.fullName(long(sip.unwrapinstance(button))) 

pop = cmds.popupMenu(mm=True, parent=name)
for location in ("N", "NW", "W", "SW", "S", "SE", "E", "NE"):
    item = cmds.menuItem(label="an option", rp=location)

widget.resize(400,300)
widget.show()