#!/usr/bin/env python
import sys
import signal
from webkit2png import WebkitRenderer
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebPage
app = QApplication(sys.argv)
signal.signal(signal.SIGINT, signal.SIG_DFL)
wkr = WebkitRenderer()

hosts = ['http://www.google.com','http://wikipedia.com','http://github.com']
for host in hosts:
    try:
        f = open(("%s.png"%host).replace('/','_'),'w')
        wkr.render_to_file(host,f)
        f.close()
        print "finished %s" % host
    except Exception,err:
        print "Error on %s: %s" % (host,str(err))
