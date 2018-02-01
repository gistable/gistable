    import sys
    from PyQt4 import QtCore, QtGui, QtWebKit
    import WebGui
     
    """Html snippet."""
    html = """
    <html><body>
     <center>
     <script language="JavaScript">
       document.write('<p>Python ' + pyObj.pyVersion + '</p>')
     </script>
     <button onClick="pyObj.showMessage('Hello from WebKit')">Press me</button>
     </center>
    </body></html>
    """
     
    class StupidClass(QtCore.QObject):
        """Simple class with one slot and one read-only property."""
     
        @QtCore.pyqtSlot(str)
        def showMessage(self, msg):
            """Open a message box and display the specified message."""
            QtGui.QMessageBox.information(None, "Info", msg)
     
        def _pyVersion(self):
            """Return the Python version."""
            return sys.version
     
        """Python interpreter version property."""
        pyVersion = QtCore.pyqtProperty(str, fget=_pyVersion)
     
     
    myObj = StupidClass()
     
    a = QtGui.qApp
    mw = a.activeWindow()
    v= mw.findChild(QtWebKit.QWebFrame)
    #v.page().currentFrame().addToJavaScriptWindowObject('pyObj', myObj)
    #v.addToJavaScriptWindowObject('pyObj', myObj)
    v.setHtml(html)
    curr1 = v.page()
    frame1 = curr1.currentFrame()
    frame1.addToJavaScriptWindowObject("pyObj", myObj)
