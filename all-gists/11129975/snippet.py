from PyQt4.QtCore import QRect
from PyQt4.QtGui import QApplication, QWidget, QLabel

class DraggableLabel( QLabel ):
    """
    A QLabel subclass that can be dragged around within its parent widget.
    Note: Not intended to work if the parent widget has a layout (e.g. QVBoxLayout).
    """
    
    def __init__(self, *args, **kwargs):
        super( DraggableLabel, self ).__init__(*args, **kwargs)
        self._dragging = False

    def mousePressEvent(self, event):
        self._dragging = True
    
    def mouseReleaseEvent(self, event):
        self._dragging = False
    
    def mouseMoveEvent(self, event):
        if not self._dragging:
            return
        
        new_pos_global = event.globalPos()
        new_pos_within_parent = self.parent().mapFromGlobal( new_pos_global )
        new_geometry = QRect( new_pos_within_parent, self.geometry().size() )
        self.setGeometry( new_geometry )

if __name__ == "__main__":
    app = QApplication([])
    
    w = QWidget()
    label = DraggableLabel("Label!", parent=w)
    w.show()
    w.raise_()        

    app.exec_()
