#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""PDF Conversor powered by Qt5."""


from uuid import uuid4

from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkProxyFactory
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWebKitWidgets import QWebView


class QPDF(QPrinter):

    """QPDF Printer."""

    def __init__(self, *args):
        """Initialize QPDF."""
        super(QPDF, self).__init__(*args)
        self.web, self.pdf_name = QWebView(), uuid4().hex + ".pdf"
        self.to_pdf, self.url_or_path = self.convert_to_pdf, None
        self.setPageSize(QPrinter.A4)
        self.setFontEmbeddingEnabled(True)
        self.setOutputFormat(QPrinter.PdfFormat)
        self.web.settings().setDefaultTextEncoding("utf-8")
        QNetworkProxyFactory.setUseSystemConfiguration(True)
        self.setPageMargins(10, 10, 10, 10, QPrinter.Millimeter)
        self.web.loadFinished.connect(lambda: self.web.print_(self))

    def _set_input_output(self, url_or_path, fyle, landscape):
        """Set the Input and Output for the processing if they are provided."""
        self.pdf_name, self.url_or_path = fyle, url_or_path
        self.setDocName(self.pdf_name.title())
        self.setOutputFileName(self.pdf_name)
        if hasattr(self, "setPageOrientation"):  # Qt > 5.3 only
            self.setPageOrientation(int(bool(landscape)))
        self.web.load(QUrl(self.url_or_path))
        return self.pdf_name

    def convert_to_pdf(self, _url, fyle=uuid4().hex + ".pdf", landscape=False):
        """Convert to PDF file from the arguments passed, at least an URL."""
        if _url and isinstance(_url, str) and len(_url):
            return self._set_input_output(_url, fyle, landscape)


##############################################################################


if __name__ in '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    conversor = QPDF()
    conversor.convert_to_pdf("https://google.com")
    # conversor.convert_to_pdf("https://google.com", "custom_filename.pdf")
    exit(app.exec_())
