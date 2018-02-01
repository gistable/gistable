from PySide import QtGui, QtCore


def findDagWidget():
   stack = QtGui.QApplication.topLevelWidgets()
   while stack:
       widget = stack.pop()
       if widget.windowTitle() == 'Node Graph':
           # You should probably be a little safer with this return, but the actual DAG widget
           # seems to be here consistently... if not, it should be the only child of 'widget'
           # that's a QWidget instance.
           return widget.children()[-1]
       stack.extend(c for c in widget.children() if c.isWidgetType())


class PaintFilter(QtCore.QObject):
    def scribble(self, obj, event):
        qp = QtGui.QPainter()
        qp.begin(obj)
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, "Hurray")        
        qp.end()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Paint:
            # Call DAG paint event
            obj.paintEvent(event)
            # Do custom painting
            self.scribble(obj, event)
            return True

        return QtCore.QObject.eventFilter(obj, obj, event)


dag = findDagWidget()

"""
# Render DAG widget into an image
image = QtGui.QImage(dag.size(), QtGui.QImage.Format_RGB32)
dag.repaint()
dag.render(image)
image.save("/tmp/test.png")
"""

# Remove old event filter
# FIXME: Debug'y thing, for iteration in script editor
try: dag.removeEventFilter(thing)
except: pass

# Install event filter
thing=PaintFilter()
dag.installEventFilter(thing)
