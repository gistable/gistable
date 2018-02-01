def on_touch_down(self, touch, *kwargs):
    if not self.collide_point(*touch.pos):
        return
    
    touch.grab(self)
    self.touches.append(touch)
    touch.is_dragging = False
    touch.is_scrolling = False
    
    if len(self.touches)==1:
        self.browser.SendMouseClickEvent(touch.x, self.height-touch.pos[1],
                                            cefpython.MOUSEBUTTON_LEFT,
                                            mouseUp=False, clickCount=1)
    elif len(self.touches)==2:
        pass


def on_touch_move(self, touch, *kwargs):
    if touch.grab_current is not self:
        return
    
    if len(self.touches)==1:
        if (abs(touch.dx)>5 or abs(touch.dy)>5) or touch.is_dragging:
            touch.is_dragging = True
            self.browser.SendMouseMoveEvent(touch.x, self.height-touch.pos[1],
                                            mouseLeave=False)
    elif len(self.touches)==2:
        touch1, touch2 = self.touches
        dx = touch2.dx/2. + touch1.dx/2.
        dy = touch2.dy/2. + touch1.dy/2.
        if (abs(dx)>8 or abs(dy)>8) or touch.is_scrolling:
            touch.is_scrolling = True
            self.browser.SendMouseWheelEvent(touch.x, self.height-touch.pos[1], dx, -dy)
    
    
def on_touch_up(self, touch, *kwargs):
    if touch.grab_current is not self:
        return
    
    if len(self.touches)==2:
        if not touch.is_scrolling:
            self.browser.SendMouseClickEvent(touch.x, self.height-touch.pos[1],
                                                cefpython.MOUSEBUTTON_RIGHT,
                                                mouseUp=False, clickCount=1)
            self.browser.SendMouseClickEvent(touch.x, self.height-touch.pos[1],
                                                cefpython.MOUSEBUTTON_RIGHT,
                                                mouseUp=True, clickCount=1)
    else:
        self.browser.SendMouseClickEvent(touch.x, self.height-touch.pos[1],
                                        cefpython.MOUSEBUTTON_LEFT,
                                        mouseUp=True, clickCount=1)
    
    self.touches.remove(touch)
    touch.ungrab(self)