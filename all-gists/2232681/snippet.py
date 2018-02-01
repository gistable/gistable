#!/usr/bin/python
# -*- coding: utf-8 -*-

# Quick and dirty Chrome kwallet password extractor

from PyKDE4.kdeui import KWallet
from PyQt4.QtGui import QApplication
from sys import argv

app = QApplication([])
app.setApplicationName("Chrome password extractor")

wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
wallet.setFolder("Chrome Form Data") # check your wallet for exact folder name

entries = wallet.entryList()
entry = entries.filter(argv[1])[0]
entry = wallet.readEntry(entry)[1]

# outputs ugly slice of pickled data, hopefully you can eyeball the passsword from there
print(repr(str(entry[0:-1:2])))
