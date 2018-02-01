from ghost import Ghost
from PySide.QtGui import QApplication, QImage, QPainter, QPrinter

class MyGhost(Ghost):

    def capture_pdf(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setResolution(300)
        printer.setOutputFileName("QtPrinter.pdf")
        printer.setPaperSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFormat(QPrinter.PdfFormat)

        painter = QPainter(printer)
        self.main_frame.render(painter)
        painter.end()

ghost = MyGhost(viewport_size=(1280,960))

page, resources = ghost.open('http://127.0.0.1:8000/path/to/page/to/capture/')
ghost.capture_pdf()
