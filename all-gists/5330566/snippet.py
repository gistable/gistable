## The following is from TonyT
## http://hints.macworld.com/article.php?story=2008051406323031

import sys
import time
from Quartz.CoreGraphics import *    # imports all of the top-level symbols in the module

class AppleMouseEvents():
    """
     with thanks to:
     TonyT http://hints.macworld.com/article.php?story=2008051406323031
     
     example:
    m = AppleMouseEvents()
    pos = m.currentPos()
    m.mousedrag(pos.x,pos.y+float('30'))
    
    """
    def __init__(self):
        self.relative = True
        
    def mouseEvent(self,type, posx, posy):
        theEvent = CGEventCreateMouseEvent(None, type, (posx,posy), kCGMouseButtonLeft)
        CGEventPost(kCGHIDEventTap, theEvent)
    def mousemove(self,posx,posy):
        self.mouseEvent(kCGEventMouseMoved, posx,posy);
    def mouseclickdn(self,posx,posy):
        self.mouseEvent(kCGEventLeftMouseDown, posx,posy);
    def mouseclickup(self,posx,posy):
        self.mouseEvent(kCGEventLeftMouseUp, posx,posy);
    def mousedrag(self,posx,posy):
        self.mouseEvent(kCGEventLeftMouseDragged, posx,posy);
    
    def mouserclick(self,posx,posy):
        self.mouseEvent(kCGEventRightMouseDown, posx,posy);
        self.mouseEvent(kCGEventRightMouseUp, posx,posy);
    
    def mousesingleclick(self,posx,posy):
        self.mouseclickdn(posx,posy)
        self.mouseclickup(posx,posy)

    def mousedblclick(self,posx,posy):
        self.mousesingleclick(posx,posy)
        self.mousesingleclick(posx,posy)
    
    def mousetrplclick(self,posx,posy):
        self.mousesingleclick(posx,posy)
        self.mousesingleclick(posx,posy)
        self.mousesingleclick(posx,posy)
    
    def currentPos(self):
        ourEvent = CGEventCreate(None);	
        return CGEventGetLocation(ourEvent);	# Save current mouse position    

class AppleKeyboardEvents():
    def __init__(self):
        self.relative = True

class AppleWindowEvents():
    def __init__(self):
        self.relative = True
