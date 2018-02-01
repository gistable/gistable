#!/usr/bin/env python

import sys
import time

from flask import Flask
from PyQt4 import QtCore, QtGui, QtWebKit

import gevent.wsgi

class WebView(QtWebKit.QWebView):
    def __init__(self):
        QtWebKit.QWebView.__init__(self)

        self.load(QtCore.QUrl("http://localhost:5000/"))
        self.connect(self , QtCore.SIGNAL("clicked()"), self.closeEvent)

    def closeEvent(self, event):
        self.deleteLater()
        app.quit()
        print "closing gui"
        g.kill(gevent.GreenletExit, block=False)
        f.kill(gevent.GreenletExit, block=False)
        print "are gui and webserver alive? ", g.dead, f.dead


class PyQtGreenlet(gevent.Greenlet):
    def __init__(self, app):
        gevent.Greenlet.__init__(self)
        self.app = app

    def _run(self):
        while True:
            self.app.processEvents()
            while self.app.hasPendingEvents():
                self.app.processEvents()
                gevent.sleep(0.01)
        gevent.sleep(0.1)
   
if __name__ == "__main__":
    fapp = Flask(__name__)
    fapp.debug=True

    @fapp.route("/")
    def hello():
        print time.time()
        return '<a href="http://localhost:5000/bye" > quit() </a></br><a href="http://localhost:5000/" > reload </a></br>count={0}'.format(time.time())

    @fapp.route("/bye", methods=['GET'])
    def goodbye():
        print "killing webserver"
        f.kill(block=False)
        print "is webserver alive? ", f.dead
        window.closeEvent(QtCore.SIGNAL("clicked()"))
        return 'goodbye'

    http_server = gevent.wsgi.WSGIServer(('', 5000), fapp)
    f = gevent.spawn( http_server.serve_forever)

    app = QtGui.QApplication(sys.argv)  
    window = WebView()
    window.show()
    g = PyQtGreenlet.spawn(app)
    gevent.joinall([f, g])
    
