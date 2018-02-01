# -*- coding: utf-8 -*-

import requests
from PySide import QtGui, QtCore
import sys


class AddressEdit(QtGui.QLineEdit):
    def __init__(self, parent):
        QtGui.QLineEdit.__init__(self, parent)


class AddressBar(QtGui.QToolBar):
    def __init__(self, browser):
        QtGui.QToolBar.__init__(self, browser.window)
        self.setFloatable(False)
        self.setMovable(False)
        self.browser = browser
        self.address = AddressEdit(self)
        self.address.returnPressed.connect(self.inputUrl)
        self.addWidget(self.address)

    def setUrl(self, url):
        self.address.setText(url)

    def inputUrl(self):
        self.browser.load(self.address.text())


class TextBrowser(QtGui.QApplication):
    def __init__(self, argv):
        QtGui.QApplication.__init__(self, argv)
        self.window = QtGui.QMainWindow()
        self.addressBar = AddressBar(self)

        self.label = QtGui.QLabel()
        self.window.setCentralWidget(self.label)
        self.window.addToolBar(self.addressBar)
        self.window.show()
        self.load("http://hogel.org")

    def load(self, url):
        self.addressBar.setUrl(url)
        html = requests.get(url).read().decode("utf-8")
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setText(html)
        self.label.update()
        self.label.repaint()

if __name__ == '__main__':
    browser = TextBrowser(sys.argv)
    browser.exec_()
