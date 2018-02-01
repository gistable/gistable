from PySide import QtCore, QtGui
import shiboken
import maya.OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import pymel.core as pm

def wrapInstance(ptr, base=None):
    """
    Utility to convert a pointer to a Qt class instance (PySide/PyQt compatible)
    borrowed from http://nathanhorne.com/?p=485
    :param ptr: Pointer to QObject in memory
    :type ptr: long or Swig instance
    :param base: (Optional) Base class to wrap with (Defaults to QObject, which should handle anything)
    :type base: QtGui.QWidget
    :return: QWidget or subclass instance
    :rtype: QtGui.QWidget
    """
    if ptr is None:
        return None
    ptr = long(ptr)  # Ensure type
    if globals().has_key('shiboken'):
        if base is None:
            qObj = shiboken.wrapInstance(long(ptr), QtCore.QObject)
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr(QtGui, cls):
                base = getattr(QtGui, cls)
            elif hasattr(QtGui, superCls):
                base = getattr(QtGui, superCls)
            else:
                base = QtGui.QWidget
        return shiboken.wrapInstance(long(ptr), base)
    elif globals().has_key('sip'):
        base = QtCore.QObject
        return sip.wrapinstance(long(ptr), base)
    else:
        return None

layerControlName = "DisplayLayerUITabLayout"
 
class MyWidget(MayaQWidgetDockableMixin,QtGui.QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        

        ptr = omui.MQtUtil.findControl(layerControlName)

        attrWidget = wrapInstance(ptr, QtGui.QWidget)
        
        attrWidget.setObjectName("myLayerEditor")
        
        layout.addWidget(attrWidget)
        
ui = MyWidget()
ui.show()

pm.mel.source("layerEditor.mel")
