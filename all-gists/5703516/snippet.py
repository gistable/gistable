"""Test of finding Nuke's viewer widget, and intercepting the hardwired "c" shortcut and rewiring it to view the RGB channel
"""

from PySide import QtGui, QtCore


def findviewer():
    stack = QtGui.QApplication.topLevelWidgets()
    viewers = []
    while stack:
        widget = stack.pop()
        if widget.windowTitle().startswith('Viewer'):
            # TODO: More robust detection of viewer widget (verify some of the child widgets or something..?)
            viewers.append(widget)
        stack.extend(c for c in widget.children() if c.isWidgetType())

    return viewers

class KeyIntercepter(QtCore.QObject):
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key_C:
                def sendkey(key):
                    new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, key, QtCore.Qt.NoModifier)
                    QtGui.QApplication.instance().postEvent(
                       obj,
                       new_event)
                # Same as pressing "RGRR" in viewer, switches between to channels, then back to RGB
                sendkey(QtCore.Qt.Key_R)
                sendkey(QtCore.Qt.Key_G)
                sendkey(QtCore.Qt.Key_R)
                sendkey(QtCore.Qt.Key_R)

                # Event was handled..
                return True
        return QtCore.QObject.eventFilter(obj, obj, event)


viewers = findviewer()

# Remove old event filter
# FIXME: Debugging thing, for iteration in script editor
try: dag.removeEventFilter(thing)
except: pass

# Install event filter
thing=KeyIntercepter()
for v in viewers:
    v.installEventFilter(thing)
