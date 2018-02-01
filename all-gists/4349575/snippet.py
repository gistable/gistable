import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt


class DragFromWidget(QtGui.QDockWidget):

    def __init__(self, parent=None):
        super(DragFromWidget, self).__init__(parent=parent)
        self.layout().addWidget(QtGui.QLabel("Label!"))

    def dragEnterEvent(self, event):
        print("dragEnterEvent")

    def mousePressEvent(self, event):
        label = self.childAt(event.pos())
        if not label:
            return # nothing was selected
        hotSpot = event.pos() - label.pos()
        mimeData = QtCore.QMimeData()
        mimeData.setText(label.text())
        mimeData.setData("application/x-hotspot", str(hotSpot.x()))
        pixmap = QtGui.QPixmap(label.size())
        label.render(pixmap)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(hotSpot)

        dropAction = drag.exec_(Qt.CopyAction|Qt.MoveAction, Qt.CopyAction)
        if dropAction == Qt.MoveAction:
            label.close()


class DragToWidget(QtGui.QDockWidget):

    def __init__(self, parent=None):
        super(DragToWidget, self).__init__(parent=parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        print("'%s' was dropped onto me." % event)


class SandboxApp(QtGui.QApplication):

    def __init__(self, *args, **kwargs):
        super(SandboxApp, self).__init__(*args)
        self.mainwindow = MainWindow()
        self.mainwindow.show()


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setDockOptions(QtGui.QMainWindow.AllowNestedDocks|QtGui.QMainWindow.AnimatedDocks)
        self.addDockWidget(Qt.LeftDockWidgetArea, DragFromWidget())
        self.addDockWidget(Qt.RightDockWidgetArea, DragToWidget())


def main():
    app = SandboxApp(sys.argv)
    sys.exit(app.exec_())
    


if __name__ == "__main__":
    main()