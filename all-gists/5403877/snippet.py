from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as apiUI
import sys

def getMayaWindow():
    """
    Get the main Maya window as a QtGui.QMainWindow instance
    @return: QtGui.QMainWindow instance of the top level Maya windows
    """
    ptr = apiUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(long(ptr), QtGui.QMainWindow)
        
class HelloWorld(QtGui.QDialog):
    def __init__(self,  parent=getMayaWindow()):
        super(HelloWorld, self).__init__(parent)
        self.initUI()
         
    def initUI(self):
        
        # layout
        self.setLayout(QtGui.QVBoxLayout())
        
        # add tabs
        self.tab_widget = QtGui.QTabWidget()
        self.layout().addWidget(self.tab_widget)
        self.tab_widget.addTab(MyButtons(), "One")
        self.tab_widget.addTab(MyButtons(), "Two")
        self.tab_widget.addTab(MyButtons(), "Three")
 
        self.show()
        
        
class MyButtons(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MyButtons, self).__init__(parent)

        # layout
        self.setLayout(QtGui.QVBoxLayout())

        # buttons
        for name in ['One', 'Two', 'Three']:

            btn =QtGui.QPushButton(name)
            self.layout().addWidget(btn)
            btn.clicked.connect(self.buttonClicked)

    def buttonClicked(self):

        sender = self.sender()
        sys.stdout.write(sender.text() + ' was pressed\n')
        
                 
ex = HelloWorld()
