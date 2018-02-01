#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
helloqt.py
PyQt5 で Hello, world!
"""

import sys
from PyQt5 import QtWidgets

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    button = QtWidgets.QPushButton("Hello, PyQt!")
    window.setCentralWidget(button)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
