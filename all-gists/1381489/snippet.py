from PyQt4 import QtCore, QtGui

import maya.cmds as cmds
import maya.OpenMayaUI as mui

import sip


class MyDialog(QtGui.QDialog):

    def __init__(self, parent, **kwargs):
        super(MyDialog, self).__init__(parent, **kwargs)
        
        self.setObjectName("MyWindow")
        self.resize(800, 600)
        self.setWindowTitle("PyQt ModelPanel Test")

        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0,0,0,0)

        # need to set a name so it can be referenced by maya node path
        self.verticalLayout.setObjectName("mainLayout")
        
        # First use SIP to unwrap the layout into a pointer
        # Then get the full path to the UI in maya as a string
        layout = mui.MQtUtil.fullName(long(sip.unwrapinstance(self.verticalLayout)))
        cmds.setParent(layout)

        paneLayoutName = cmds.paneLayout()
        
        # Find a pointer to the paneLayout that we just created
        ptr = mui.MQtUtil.findControl(paneLayoutName)
        
        # Wrap the pointer into a python QObject
        self.paneLayout = sip.wrapinstance(long(ptr), QtCore.QObject)

        self.cameraName = cmds.camera()[0]
        self.modelPanelName = cmds.modelPanel("customModelPanel", label="ModelPanel Test", cam=self.cameraName)
        
        # Find a pointer to the modelPanel that we just created
        ptr = mui.MQtUtil.findControl(self.modelPanelName)
        
        # Wrap the pointer into a python QObject
        self.modelPanel = sip.wrapinstance(long(ptr), QtCore.QObject)

        # add our QObject reference to the paneLayout to our layout
        self.verticalLayout.addWidget(self.paneLayout)

    def showEvent(self, event):
        super(MyDialog, self).showEvent(event)

        # maya can lag in how it repaints UI. Force it to repaint
        # when we show the window.
        self.modelPanel.repaint()
                    

def show():
    # get a pointer to the maya main window
    ptr = mui.MQtUtil.mainWindow()
    # use sip to wrap the pointer into a QObject
    win = sip.wrapinstance(long(ptr), QtCore.QObject)
    d = MyDialog(win)
    d.show()

    return d


try:
    dialog.deleteLater()
except:
    pass    
dialog = show()
