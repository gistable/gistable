# Authored by sundance@ierne.eu.org as found in the following link:
# http://www.mail-archive.com/pyqt@riverbankcomputing.com/msg18928.html

import sys

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import QSizeF
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QPrinter
from PyQt4.QtGui import QImage
from PyQt4 import QtWebKit

class WebKitPDF ( QObject ):

  def __init__ ( self, url, dest ):
    QObject.__init__ ( self )
    self.dest = dest
    self.page = QtWebKit.QWebPage ( self )
    self.mainFrame = self.page.mainFrame()
    self.mainFrame.load ( QUrl ( url ) )

    self.connect ( self.page,
             SIGNAL ( "loadProgress(int)" ),
             self.loadProgress )

    self.connect ( self.page,
             SIGNAL ( "loadFinished(bool)" ),
             self.renderPDF )



  def loadProgress ( self, progress ):
    print "Progress: ", progress


  def renderPDF ( self, status ):
    print "Load finished with status: ", status
    print "Rendering PDF ..."

    contentsSize = self.mainFrame.contentsSize()
    self.page.setViewportSize ( contentsSize )

    self.printer = QPrinter ( QPrinter.PrinterResolution )
    #self.printer = QPrinter ( QPrinter.ScreenResolution )
    self.printer.setOutputFormat ( QPrinter.PdfFormat )
    #self.printer.setPaperSize ( QPrinter.A4 )
    self.printer.setFullPage( True )
    self.printer.setPaperSize ( QSizeF( contentsSize ), QPrinter.DevicePixel )
    self.printer.setOrientation ( QPrinter.Portrait )
    self.printer.setOutputFileName ( self.dest )

    self.painter = QPainter ( self.printer )
    self.painter.setRenderHint ( QPainter.Antialiasing )
    self.mainFrame.render ( self.painter )
    self.painter.end()
    app = QtGui.QApplication.instance()
    app.exit ( 0 )
    
    

def main( url, dest ):
  app = QtGui.QApplication ( sys.argv )
  wk = WebKitPDF ( url, dest )
  sys.exit ( app.exec_() )


if __name__ == "__main__":

  import sys

  try:
    url  = sys.argv[1]
    dest = sys.argv[2]

  except IndexError:
    sys.exit()

  main( url, dest )