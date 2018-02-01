"""Illustration of how to retrieve the shape under the mouse cursor

Usage:
  Run `start()` to start listening for when the mouse stops and to display a tooltip
  Run `stop()` to stop listening

"""

from maya import cmds
from PySide import QtGui, QtCore

data = {
    "lastPosition": QtCore.QPoint(0, 0),
    "currentTooltip": None,
    "timer": None
}

def tooltip(message):
    """Produce tooltip"""
    tooltip = QtGui.QLabel(message)
    tooltip.setWindowFlags(QtCore.Qt.ToolTip)
    tooltip.setStyleSheet("""
    QLabel {
        background: "white";
        color: "black";
        height: 30px;
        width: 100px;
        padding: 20px;
        border: 2px solid black;
    }
    """)
    tooltip.move(QtGui.QCursor.pos())
    tooltip.show()

    QtCore.QTimer.singleShot(2000, tooltip.deleteLater)
    
    # Store reference    
    data["currentTooltip"] = tooltip

def evaluate():
    """Should we produce a tooltip?"""
    position = QtGui.QCursor.pos()

    if position == data["lastPosition"]:
        object = object_under_cursor()

        if not object:
            return

        tooltip('"{}" is of type "{}"'.format(
            object, cmds.nodeType(object)))

    data["lastPosition"] = position

def object_under_cursor():
    """Get objects under cursor"""
    pos = QtGui.QCursor.pos()
    widget = QtGui.qApp.widgetAt(pos)
    relpos = widget.mapFromGlobal(pos)

    panel = cmds.getPanel(underPointer=True) or ""
    
    if not "modelPanel" in panel:
        return

    return (cmds.hitTest(panel, relpos.x(), relpos.y()) or [None])[0]

def start():
    """Track the cursor"""
    if data["timer"] is not None:
        data["timer"].stop()

    timer = QtCore.QTimer()
    timer.setInterval(1001)
    timer.timeout.connect(evaluate)
    timer.start()
    
    # Store reference
    data["timer"] = timer

def stop():
    if data["timer"] is not None:
        data["timer"].stop()
        data["timer"] = None

start()
#stop()