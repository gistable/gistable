
from PySide import QtGui

def grab_widget(widget=None, filepath=None):
    """This is a test and is not proofed for production

    Note:
        See QPixmap members being obsolete in Qt5:
        http://doc.qt.io/qt-5/qpixmap-obsolete.html
    """
    try:
        screenshot = QtWidgets.QWidget.grab(widget)  # Qt5
    except:
        screenshot = QtGui.QPixmap.grabWidget(widget)  # Qt4
    if filepath:
        screenshot.save(filepath, 'png')


def grab_desktop(filepath=None):
    """Grab the entire desktop and save as PNG"""
    app = QtGui.QApplication.instance()
    screenshot = QtGui.QPixmap.grabWindow(app.desktop().winId())
    if filepath:
        screenshot.save(filepath, 'png')


def grab_window(window_id, filepath=None):
    """Grab the given window by its id

    Example usage:
        grab_window(window_id=widget.winId())

    Note:
        In Qt5, QPixmap.grabWindow is obsolete and instead we should use
        QScreen.grabWindow. This is, however, not possible yet in
        PySide2.
        Read more: http://doc.qt.io/qt-5/qpixmap-obsolete.html
    """
    screenshot = QtGui.QPixmap.grabWindow(window_id)  # Qt4
    if filepath:
        screenshot.save(filepath, 'png')


def find_viewers():
    """Return all viewer widgets"""
    stack = QtGui.QApplication.topLevelWidgets()
    viewers = []
    while stack:
        widget = stack.pop()
        if widget.objectName().startswith('Viewer.'):
            viewers.append(widget)
        stack.extend(c for c in widget.children() if c.isWidgetType())
    return viewers


viewer_widgets = find_viewers()
if len(viewer_widgets) > 0:
    widget = viewer_widgets[0]
    grab_desktop(filepath=os.path.expanduser('~/Desktop/screengrab_desktop.png'))
    grab_widget(widget=widget, filepath=os.path.expanduser('~/Desktop/screengrab_widget.png'))
    grab_window(window_id=widget.winId(), filepath=os.path.expanduser('~/Desktop/screengrab_window.png'))