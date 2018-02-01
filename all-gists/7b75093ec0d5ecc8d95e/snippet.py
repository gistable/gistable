import maya.mel as mel
import maya.OpenMayaUI as omui
from PySide.QtGui import *
from PySide.QtCore import *
from shiboken import wrapInstance as wrap
qMaya = wrap(long(omui.MQtUtil.mainWindow()), QMainWindow)
   
# find chennelbox
gChannelBoxName = mel.eval('$temp=$gChannelBoxName')
table = qMaya.findChild(QTableView, gChannelBoxName)
if table:
    model = table.model()
else:
    model = None
 
# main function
def selectChannelBoxAttr(attrArray):
    if model:
    	table.setSelectionMode( QAbstractItemView.MultiSelection );
        table.clearSelection()
        for atr in attrArray:
            for i in range(model.rowCount()):
                if atr ==  model.data(model.index(i,0)):
                    table.selectRow(i)
 
# ############################ test
attrs = ['Scale Y', 'Translate X']
selectChannelBoxAttr(attrs)