# -*- coding: utf-8 -*-

#PyQt4.QtGui imports
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QCursor

#PyQt4.QtGui imports
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QTextCodec


#sys import
import sys


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Custom Menu")

        self.text_edit = QTextEdit()
        self.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)

        self.setCentralWidget(self.text_edit)

        self.connect(self.text_edit, SIGNAL('customContextMenuRequested(const QPoint &)'), self.context_menu)

    def context_menu(self):
        menu = QMenu(self)
        menu.addAction("Primera opción")
        menu.addAction("Segunda opción")
        menu.addAction(":)")
        menu.exec_(QCursor.pos())


#Init Qt Application
app = QApplication(sys.argv)

QTextCodec.setCodecForCStrings(QTextCodec.codecForName('utf-8'))

window = MainWindow()
window.show()

sys.exit(app.exec_())