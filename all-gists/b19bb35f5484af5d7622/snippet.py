import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from nukescripts import panels

class PanelTest(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout())
        self.myTable    = QtGui.QTableWidget()
        self.myTable.header = ['Date', 'Files', 'Size', 'Path' ]
        self.myTable.size = [ 75, 375, 85, 600 ]
        self.myTable.setColumnCount(len(self.myTable.header))
        self.myTable.setHorizontalHeaderLabels(self.myTable.header)
        self.myTable.setSelectionMode(QtGui.QTableView.ExtendedSelection)
        self.myTable.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.myTable.setSortingEnabled(1)
        self.myTable.sortByColumn(1, QtCore.Qt.DescendingOrder)
        self.myTable.setAlternatingRowColors(True)

        self.myTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.myTable.setRowCount(50)
        self.layout().addWidget(self.myTable)

        self.myTable.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        def closeEvent():
            print 'Closed PanelTest'

class mainPanel(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.testBtn = QtGui.QPushButton()
        self.setLayout( QtGui.QVBoxLayout() )
        self.layout().addWidget( self.testBtn )
        self.testBtn.clicked.connect(self.createPanel)
        self.setSizePolicy( QtGui.QSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

    def closeEvent():
        print 'Closed mainPanel'

    def createPanel(self):
        pane = nuke.getPaneFor("example.test.panel")
        print pane
        panels.registerWidgetAsPanel('PanelTest', 'PanelTest',"example.test.panel", True).addToPane(pane)

mp = mainPanel()
mp.createPanel()