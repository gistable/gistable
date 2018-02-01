from PyQt4 import QtCore, QtGui

class ColorBox(QtGui.QFrame):

    def __init__(self,parent=None):
        super(ColorBox,self).__init__(parent)
        
        self.bgColor = QtCore.Qt.white      
        self.setFixedHeight(20)
        self.setFrameStyle(1)
        self.setStyleSheet("QWidget { border-color: rgba(0,0,0,0)}")
       
    def mousePressEvent(self, e):
        if e.buttons() == QtCore.Qt.LeftButton:
            col = QtGui.QColorDialog.getColor(self.bgColor, self)
   
            if col.isValid():
                rgb = (col.red(), col.green(), col.blue())
                self.setStyleSheet("QWidget { background-color: rgb(%d,%d,%d) }" % rgb)
                self.bgColor = col


if __name__ == "__main__":
    app = QtGui.QApplication([])
    c = ColorBox()
    c.show()
    app.exec_()