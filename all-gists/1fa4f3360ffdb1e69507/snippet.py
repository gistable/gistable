from PySide import QtCore, QtGui
import sys

app = QtGui.QApplication(sys.argv)
QtGui.qApp = app

folderTree = QtGui.QTreeWidget()

header = QtGui.QTreeWidgetItem(["Virtual folder tree","Comment"])
#...
folderTree.setHeaderItem(header)   #Another alternative is setHeaderLabels(["Tree","First",...])

root = QtGui.QTreeWidgetItem(folderTree, ["Untagged files"])
root.setData(2, QtCore.Qt.EditRole, 'Some hidden data here')	# Data set to column 2, which is not visible

folder1 = QtGui.QTreeWidgetItem(root, ["Interiors"])
folder1.setData(2, QtCore.Qt.EditRole, 'Some hidden data here')	# Data set to column 2, which is not visible

folder2 = QtGui.QTreeWidgetItem(root, ["Exteriors"])
folder2.setData(2, QtCore.Qt.EditRole, 'Some hidden data here')	# Data set to column 2, which is not visible

folder1_1 = QtGui.QTreeWidgetItem(folder1, ["Bathroom", "Seg was here"])
folder1_1.setData(2, QtCore.Qt.EditRole, 'Some hidden data here')	# Data set to column 2, which is not visible

folder1_2 = QtGui.QTreeWidgetItem(folder1, ["Living room", "Approved by client"])
folder1_2.setData(2, QtCore.Qt.EditRole, 'Some hidden data here')	# Data set to column 2, which is not visible



def printer( treeItem ):
	foldername = treeItem.text(0)
	comment = treeItem.text(1)
	data = treeItem.text(2)
	print foldername + ': ' + comment + ' (' + data + ')'


folderTree.itemClicked.connect( lambda : printer( folderTree.currentItem() ) )


folderTree.show()
sys.exit(app.exec_())