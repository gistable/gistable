# NOTE: this script stops when esc key pressed not to freeze c4d because of some heavy codes.

import c4d
from c4d import gui

def frame( f ):
    # exec some processing..
    pass

def escPressed():
    bc = c4d.BaseContainer()
    rs = gui.GetInputState( c4d.BFM_INPUT_KEYBOARD, c4d.KEY_ESC, bc )
    if rs and bc[ c4d.BFM_INPUT_VALUE ]:
        return True
    return False

def main():
    doc = c4d.documents.GetActiveDocument()
    fps = doc[ c4d.DOCUMENT_FPS ]
    minTime = doc[ c4d.DOCUMENT_MINTIME ].GetFrame( fps )
    maxTime = doc[ c4d.DOCUMENT_MAXTIME ].GetFrame( fps )

    f = 0
    for f in range( minTime, maxTime ):
        doc.SetTime( c4d.BaseTime( f, fps ) )
        c4d.DrawViews( c4d.DA_ONLY_ACTIVE_VIEW|c4d.DA_NO_THREAD|c4d.DA_NO_REDUCTION|c4d.DA_STATICBREAK )
        c4d.GeSyncMessage( c4d.EVMSG_TIMECHANGED )
        c4d.EventAdd( c4d.EVENT_ANIMATE )
        frame( f )
        if escPressed():
            break
    
    gui.MessageDialog( "%i - %i frames processed." % (minTime, f) )
    
if __name__=='__main__':
    main()
