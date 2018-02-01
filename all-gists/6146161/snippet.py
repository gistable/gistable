import sys
from PyQt4 import QtCore, QtGui

class TabPlainTextEdit(QtGui.QTextEdit):
    def __init__(self,parent):
        QtGui.QTextEdit.__init__(self, parent)

    def keyPressEvent(self, event):
        # Shift + Tab is not the same as trying to catch a Shift modifier and a tab Key.
        # Shift + Tab is a Backtab!!
        if event.key() == QtCore.Qt.Key_Backtab:
            cur = self.textCursor()
            # Copy the current selection
            pos = cur.position() # Where a selection ends
            anchor = cur.anchor() # Where a selection starts (can be the same as above)

            # Can put QtGui.QTextCursor.MoveAnchor as the 2nd arg, but this is the default
            cur.setPosition(pos) 

            # Move the position back one, selection the character prior to the original position
            cur.setPosition(pos-1,QtGui.QTextCursor.KeepAnchor)
            
            if str(cur.selectedText()) == "\t":
                # The prior character is a tab, so delete the selection
                cur.removeSelectedText()
                # Reposition the cursor with the one character offset
                cur.setPosition(anchor-1)
                cur.setPosition(pos-1,QtGui.QTextCursor.KeepAnchor)
            else:
                # Try all of the above, looking before the anchor (This helps if the achor is before a tab)
                cur.setPosition(anchor) 
                cur.setPosition(anchor-1,QtGui.QTextCursor.KeepAnchor)
                if str(cur.selectedText()) == "\t":
                    cur.removeSelectedText()
                    cur.setPosition(anchor-1)
                    cur.setPosition(pos-1,QtGui.QTextCursor.KeepAnchor)
                else:

                    # Its not a tab, so reset the selection to what it was
                    cur.setPosition(anchor)
                    cur.setPosition(pos,QtGui.QTextCursor.KeepAnchor)
        else:
            return QtGui.QTextEdit.keyPressEvent(self, event)

def main():
    app = QtGui.QApplication(sys.argv)
    w = TabPlainTextEdit(None)
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
