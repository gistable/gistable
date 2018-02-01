from kivy.factory import Factory
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.properties import *
from kivy.graphics import *


class SlideShow(Widget):
    slide = StringProperty('')
    slides = ListProperty([])
    index = NumericProperty(0)
    offset = NumericProperty(0)
    
    
    def __init__(self, **kwargs):
        super(SlideShow, self).__init__(**kwargs)
        self.slide_touch = (0,0)
        self.gfx = []

    def slide_left(self, *args):
        anim = Animation(offset=self.width, t='out_quad', d=0.5)
        anim.start(self)


    def slide_right(self, *args):
        anim = Animation(offset=-self.width, t='out_quad', d=0.5)
        anim.start(self)

    def on_slides(self, *args):
        self.canvas.clear()
        self.gfx = []
        x,y = -self.width,0
        with self.canvas:
            for s in self.slides:
                g = Rectangle(size=self.size,pos=(x,0), source=s)
                self.gfx.append(g)
                x += self.width

        self.slide_left()

    def on_offset(self, *args):
        if self.offset >= self.width:
            self.offset = 0
            self.gfx[0].pos = (self.width,0)
            self.gfx[1].pos = (self.width,0)
            self.gfx[-1].pos = (self.width,0)
            self.gfx.insert(0,self.gfx.pop())
        if self.offset <= -self.width:
            self.offset = 0
            self.gfx[0].pos = (self.width,0)
            self.gfx[1].pos = (self.width,0)
            self.gfx[-1].pos = (self.width,0)
            self.gfx.append(self.gfx.pop(0))
        self.gfx[0].pos = (-self.width+self.offset, 0)
        self.gfx[1].pos = (self.offset, 0)
        self.gfx[2].pos = (self.width + self.offset, 0)
        self.slide = self.gfx[1].source

    def on_touch_down(self, touch):
        self.slide_touch = (touch.uid, touch.x)
        return True

    def on_touch_move(self, touch):
        tuid,x = self.slide_touch
        if touch.uid == tuid:
            self.offset += touch.dx
            self.slide_touch = (touch.uid, touch.x)
        self.canvas.ask_update()
        return True

    def on_touch_up(self, touch):
        tuid,x = self.slide_touch
        if touch.uid == tuid:
            target = 0
            edge = self.width * 0.3
            if self.offset < - edge: 
                target = -self.width
            if self.offset > edge:
                target = self.width
            anim = Animation(offset=target, t='out_quad', d=0.5)
            anim.start(self)
        return True

Factory.register('SlideShow', SlideShow)