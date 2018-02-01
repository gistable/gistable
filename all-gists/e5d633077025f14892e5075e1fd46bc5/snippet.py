"""Render HTML for scraping"""
# -*- coding: utf-8 -*-

import os
import sys
from contextlib import contextmanager
from multiprocessing import Pool

try:
    TimeoutError
except NameError:
    from multiprocessing import TimeoutError  # Python 2


def _render(source_html):
    """Return rendered HTML."""
    try:
        from PyQt5.QtCore import QEventLoop
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        from PyQt5.QtWidgets import QApplication

        class Render(QWebEngineView):
            """Render HTML with PyQt5 WebEngine."""

            def __init__(self, html):
                self.html = None
                self.app = QApplication(sys.argv)
                QWebEngineView.__init__(self)
                self.loadFinished.connect(self._loadFinished)
                self.setHtml(html)
                while self.html is None:
                    self.app.processEvents(
                        QEventLoop.ExcludeUserInputEvents |
                        QEventLoop.ExcludeSocketNotifiers |
                        QEventLoop.WaitForMoreEvents)
                self.app.quit()

            def _callable(self, data):
                self.html = data

            def _loadFinished(self, result):
                self.page().toHtml(self._callable)
    except ImportError:
        from PyQt5.QtWebKitWidgets import QWebPage
        from PyQt5.QtWidgets import QApplication

        class Render(QWebPage):
            """Render HTML with PyQt5 WebKit."""

            def __init__(self, html):
                self.html = None
                self.app = QApplication(sys.argv)
                QWebPage.__init__(self)
                self.loadFinished.connect(self._loadFinished)
                self.mainFrame().setHtml(html)
                self.app.exec_()

            def _loadFinished(self, result):
                self.html = self.mainFrame().toHtml()
                self.app.quit()

    with devnull():
        return Render(source_html).html


@contextmanager
def devnull():
    """Temporarily redirect stdout and stderr to /dev/null."""

    try:
        original_stderr = os.dup(sys.stderr.fileno())
        original_stdout = os.dup(sys.stdout.fileno())
        null = open(os.devnull, 'w')
        os.dup2(null.fileno(), sys.stderr.fileno())
        os.dup2(null.fileno(), sys.stdout.fileno())
        yield

    finally:
        if original_stderr is not None:
            os.dup2(original_stderr, sys.stderr.fileno())
        if original_stdout is not None:
            os.dup2(original_stdout, sys.stdout.fileno())
        if null is not None:
            null.close()


def render(html):
    """Perform render in a new process to prevent hangs."""

    tries = 3

    for _ in range(tries):
        pool = Pool(1)
        try:
            return pool.apply_async(_render, args=(html,)).get(timeout=120)
        except TimeoutError:
            continue
        finally:
            pool.terminate()

    raise TimeoutError('Timed out attempting to render HTML %d times' % tries)
