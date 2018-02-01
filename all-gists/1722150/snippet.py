'''
original from http://nathanhorne.com/?p=183
'''
import os
import sip
import maya.cmds as cmds
import maya.OpenMayaUI as mui
from PyQt4 import QtGui, QtCore, uic

def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

uiFile = os.path.join(cmds.internalVar(uwd=True), 'ui', 'form.ui')
form_class, base_class = uic.loadUiType(uiFile)

class Window(base_class, form_class):
    def __init__(self, parent=getMayaWindow()):
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        self.setObjectName('myTool')
        self.setWindowTitle("My Qt Tool Window")
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.pushButton.clicked.connect(self.click)
	
    def click(self):
        cmds.sphere();

def main():
    global myWindow
    try:
        myWindow.close()
    except:
        pass
    myWindow = Window()
    myWindow.show()
