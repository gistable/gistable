import sys
from PyQt4.QtCore import (pyqtSlot, pyqtSignal, QObject, QSize, QUrl,
                          SIGNAL)
from PyQt4.QtGui import (QApplication, QImage, QPainter)
from PyQt4.QtWebKit import QWebPage

class Thumbnailer(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

        self.webPage = QWebPage(self)
        self.mainFrame = self.webPage.mainFrame()

        self.webPage.loadFinished.connect(self.render)

    def load(self, url):
        qurl = QUrl(url)
        self.webPage.mainFrame().load(qurl)

    def render(self):
        self.webPage.setViewportSize(self.webPage.mainFrame().contentsSize())
        image = QImage(self.webPage.viewportSize(), QImage.Format_ARGB32)

        painter = QPainter()
        painter.begin(image)
        self.webPage.mainFrame().render(painter)
        painter.end()

        image.save('thumbnail.png')
        self.finished.emit()
 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    thumbnail = Thumbnailer()
    thumbnail.finished.connect(app.quit)
    thumbnail.load(sys.argv[1] if len(sys.argv) == 2 else 'http://www.hfut.edu.cn')
    app.exec_()
    
