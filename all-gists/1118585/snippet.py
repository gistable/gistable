from progress_ui import Ui_Dialog
from PyQt4 import QtCore, QtGui
import sys, time

class mythread(QtCore.QThread):
    def __init__(self,parent,n):
        QtCore.QThread.__init__(self,parent) 
        self.n=n

    def run(self):
        self.emit(QtCore.SIGNAL("total(PyQt_PyObject)"),self.n)
        i=0
        while (i<self.n):
            if (time.time() % 1==0):
                i+=1
                #print str(i)
                self.emit(QtCore.SIGNAL("update()"))

# create the dialog for zoom to point
class progress(QtGui.QDialog):
    def __init__(self): 
        QtGui.QDialog.__init__(self) 
        # Set up the user interface from Designer. 
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.progressBar.setValue(0)
        self.t=mythread(self,100)
        QtCore.QObject.connect(self.t, QtCore.SIGNAL("total(PyQt_PyObject)"), self.total)
        QtCore.QObject.connect(self.t, QtCore.SIGNAL("update()"), self.update)
        self.n=0
        self.t.start()
    def update(self):
        self.n+=1
        print self.n
        self.ui.progressBar.setValue(self.n)
    def total(self,total):
        self.ui.progressBar.setMaximum(total)

if __name__=="__main__":
    app = QtGui.QApplication([])
    c=progress()
    c.show()
    sys.exit(app.exec_())