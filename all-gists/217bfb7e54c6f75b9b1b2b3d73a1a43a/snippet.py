"""
This is what you need to do in order to get a qt window to dock next to maya channel box,
In all maya versions, including 2017 with PySide2
"""
__author__ = "liorbenhorin@gmail.com"

import sys
import os
import logging
import xml.etree.ElementTree as xml
from cStringIO import StringIO

# Qt is a project by Marcus Ottosson ---> https://github.com/mottosso/Qt.py
from Qt import QtGui, QtWidgets, QtCore, QtCompat

try:
    import pysideuic
    from shiboken import wrapInstance

    logging.Logger.manager.loggerDict["pysideuic.uiparser"].setLevel(logging.CRITICAL)
    logging.Logger.manager.loggerDict["pysideuic.properties"].setLevel(logging.CRITICAL)
except ImportError:
    import pyside2uic as pysideuic
    from shiboken2 import wrapInstance

    logging.Logger.manager.loggerDict["pyside2uic.uiparser"].setLevel(logging.CRITICAL)
    logging.Logger.manager.loggerDict["pyside2uic.properties"].setLevel(logging.CRITICAL)

import maya.OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.cmds as cmds


def loadUiType(uiFile):
    """
	:author: Jason Parks
	Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
	and then execute it in a special frame to retrieve the form_class.
	"""
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        pysideuic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        # Fetch the base_class and form class based on their type in the xml from designer
        form_class = frame['Ui_%s' % form_class]
        base_class = getattr(QtWidgets, widget_class)
    return form_class, base_class


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def maya_api_version():
    return int(cmds.about(api=True))

class MyDockingWindow(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    MAYA2014 = 201400
    MAYA2015 = 201500
    MAYA2016 = 201600
    MAYA2016_5 = 201650
    MAYA2017 = 201700

    def __init__(self, parent=None):

        self.deleteInstances()  # remove any instance of this window before starting

        super(MyDockingWindow, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.Tool)

        """
		compile the .ui file on loadUiType(), a function that uses pysideuic / pyside2uic to compile .ui files
		"""
        uiFile = os.path.join(os.path.dirname(__file__), 'MyDockingWindow_ui.ui')
        form_class, base_class = loadUiType(uiFile)
        self.ui = form_class()
        self.ui.setupUi(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def dockCloseEventTriggered(self):
        self.deleteInstances()

    # Delete any instances of this class
    def deleteInstances(self):

        def delete2016():
            # Go through main window's children to find any previous instances
            for obj in maya_main_window().children():

                if str(type(
                        obj)) == "<class 'maya.app.general.mayaMixin.MayaQDockWidget'>":  # ""<class 'maya.app.general.mayaMixin.MayaQDockWidget'>":

                    if obj.widget().__class__.__name__ == "MyDockingWindow":  # Compare object names

                        obj.setParent(None)
                        obj.deleteLater()

        def delete2017():
            '''
			Look like on 2017 this needs to be a little diffrents, like in this function,
			However, i might be missing something since ive done this very late at night :)
			'''

            for obj in maya_main_window().children():

                if str(type(obj)) == "<class '{}.MyDockingWindow'>".format(os.path.splitext(
                        os.path.basename(__file__)[0])):  # ""<class 'moduleName.mayaMixin.MyDockingWindow'>":

                    if obj.__class__.__name__ == "MyDockingWindow":  # Compare object names

                        obj.setParent(None)
                        obj.deleteLater()

        if maya_api_version() < MyDockingWindow.MAYA2017:
            delete2016()
        else:
            delete2017()

    def deleteControl(self, control):

        if cmds.workspaceControl(control, q=True, exists=True):
            cmds.workspaceControl(control, e=True, close=True)
            cmds.deleteUI(control, control=True)

    # Show window with docking ability
    def run(self):
        '''
		2017 docking is a little different...
		'''

        def run2017():
            self.setObjectName("MyMainDockingWindow")

            # The deleteInstances() dose not remove the workspace control, and we need to remove it manually
            workspaceControlName = self.objectName() + 'WorkspaceControl'
            self.deleteControl(workspaceControlName)

            # this class is inheriting MayaQWidgetDockableMixin.show(), which will eventually call maya.cmds.workspaceControl.
            # I'm calling it again, since the MayaQWidgetDockableMixin dose not have the option to use the "tabToControl" flag,
            # which was the only way i found i can dock my window next to the channel controls, attributes editor and modelling toolkit.
            self.show(dockable=True, area='right', floating=False)
            cmds.workspaceControl(workspaceControlName, e=True, ttc=["AttributeEditor", -1], wp="preferred", mw=420)
            self.raise_()

            # size can be adjusted, of course
            self.setDockableParameters(width=420)

        def run2016():
            self.setObjectName("MyMainDockingWindow")
            # on maya < 2017, the MayaQWidgetDockableMixin.show() magiclly docks the window next
            # to the channel controls, attributes editor and modelling toolkit.
            self.show(dockable=True, area='right', floating=False)
            self.raise_()
            # size can be adjusted, of course
            self.setDockableParameters(width=420)
            self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
            self.setMinimumWidth(420)
            self.setMaximumWidth(600)

        if maya_api_version() < MyDockingWindow.MAYA2017:
            run2016()
        else:
            run2017()


def show():
    '''
	this is the funciton that start things up
	'''
    global MyDockingWindow
    MyDockingWindow = MyDockingWindow(parent=maya_main_window())
    MyDockingWindow.run()
    return MyDockingWindow
