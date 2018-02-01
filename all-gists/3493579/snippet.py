from PySide import QtCore, QtGui
import sys
matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MatplotlibWidget(FigureCanvas):

    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(Figure())

        self.setParent(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        
        self.data = np.random.random((10,10))
        
        self.data = np.zeros((10,10))
        self.data[2:3,:] = 1
        self.axes.imshow(self.data)
        
    def Plot(self):
        self.data = np.random.random((10,10))
        self.axes.imshow(self.data)

# the majority of the following class comes from using 'pyside-uic blah.ui'  
# where blah.ui is a simple gui made in the qt designer

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(310, 230, 114, 32))

        self.pushButton.setObjectName("pushButton")

# change this line to use the matplotlib widget instead of the stock 'widget'
# that is in qt designer
#        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget = MatplotlibWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(150, 309, 281, 181))
        self.widget.setObjectName("widget")
        self.widget.mpl_connect('button_press_event', self.printoutput)

        self.textEdit = QtGui.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(200, 110, 341, 31))
        self.textEdit.setObjectName("textEdit")

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "clickme", None, QtGui.QApplication.UnicodeUTF8))
        self.textEdit.setHtml(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">testing</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))


    # the rest of this class was hand coded
        self.pushButton.clicked.connect(self.output)
        self.count = 0
    
    def printoutput(self, event):
        sys.stdout.flush()
        print self.widget.data[int(0.5+event.ydata), int(0.5+event.xdata)]
        sys.stdout.flush()
        
    def output(self):
        print ui.textEdit.toPlainText()
        self.count += 1
        self.widget.Plot()
        self.widget.draw()
     
try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    pass

MainWindow = QtGui.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
app.exec_()

# one nice thing is that 'ui' will still contain values created during execution of the gui (including data)