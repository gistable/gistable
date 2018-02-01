from collections import deque
from math import sin, cos, pi, atan2, hypot
import random
import time
import wx

SIZE = 600
COUNT = 64
SPEED = 100
FOLLOWERS = 4

COLORS = [
    wx.RED,
]

class Bot(object):
    def __init__(self, position, target):
        self.position = position
        self.target = target
        self.speed = random.random() + 0.5
        self.padding = random.random() * 8 + 16
        self.history = deque(maxlen=64)
    def get_position(self, offset):
        px, py = self.position
        tx, ty = self.target
        angle = atan2(ty - py, tx - px)
        return (px + cos(angle) * offset, py + sin(angle) * offset)
    def update(self, bots):
        px, py = self.position
        tx, ty = self.target
        angle = atan2(ty - py, tx - px)
        dx = cos(angle)
        dy = sin(angle)
        for bot in bots:
            if bot == self:
                continue
            x, y = bot.position
            d = hypot(px - x, py - y) ** 2
            p = bot.padding ** 2
            angle = atan2(py - y, px - x)
            dx += cos(angle) / d * p
            dy += sin(angle) / d * p
        angle = atan2(dy, dx)
        magnitude = hypot(dx, dy)
        return angle, magnitude
    def set_position(self, position):
        self.position = position
        if not self.history:
            self.history.append(self.position)
            return
        x, y = self.position
        px, py = self.history[-1]
        d = hypot(px - x, py - y)
        if d >= 10:
            self.history.append(self.position)

class Model(object):
    def __init__(self, width, height, count):
        self.width = width
        self.height = height
        self.bots = self.create_bots(count)
    def create_bots(self, count):
        result = []
        for i in range(count):
            position = self.select_point()
            target = self.select_point()
            bot = Bot(position, target)
            result.append(bot)
        return result
    def select_point(self):
        cx = self.width / 2.0
        cy = self.height / 2.0
        radius = min(self.width, self.height) * 0.4
        angle = random.random() * 2 * pi
        x = cx + cos(angle) * radius
        y = cy + sin(angle) * radius
        return (x, y)
    def update(self, dt):
        data = [bot.update(self.bots) for bot in self.bots]
        for bot, (angle, magnitude) in zip(self.bots, data):
            speed = min(1, 0.2 + magnitude * 0.8)
            dx = cos(angle) * dt * SPEED * bot.speed * speed
            dy = sin(angle) * dt * SPEED * bot.speed * speed
            px, py = bot.position
            tx, ty = bot.target
            bot.set_position((px + dx, py + dy))
            if hypot(px - tx, py - ty) < 10:
                bot.target = self.select_point()
        for bot in self.bots[-FOLLOWERS:]:
            bot.target = self.bots[0].get_position(10)

class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent)
        self.model = Model(SIZE, SIZE, COUNT)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.timestamp = time.time()
        self.on_timer()
    def on_timer(self):
        now = time.time()
        dt = now - self.timestamp
        self.timestamp = now
        self.model.update(dt)
        self.Refresh()
        wx.CallLater(10, self.on_timer)
    def on_left_down(self, event):
        self.model.bots[0].target = event.GetPosition()
    def on_right_down(self, event):
        width, height = self.GetClientSize()
        self.model = Model(width, height, COUNT)
    def on_size(self, event):
        width, height = self.GetClientSize()
        self.model = Model(width, height, COUNT)
        event.Skip()
        self.Refresh()
    def on_paint(self, event):
        n = len(COLORS)
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.BLACK_BRUSH)
        dc.Clear()
        dc.SetPen(wx.BLACK_PEN)
        for index, bot in enumerate(self.model.bots[:n]):
            dc.SetBrush(wx.Brush(COLORS[index]))
            for x, y in bot.history:
                dc.DrawCircle(x, y, 3)
        dc.SetBrush(wx.BLACK_BRUSH)
        for index, bot in enumerate(self.model.bots[:n]):
            dc.SetPen(wx.Pen(COLORS[index]))
            x, y = bot.target
            dc.DrawCircle(x, y, 6)
        for index, bot in enumerate(self.model.bots):
            dc.SetPen(wx.BLACK_PEN)
            if index < n:
                dc.SetBrush(wx.Brush(COLORS[index]))
            elif index >= COUNT - FOLLOWERS:
                dc.SetBrush(wx.BLACK_BRUSH)
                dc.SetPen(wx.WHITE_PEN)
            else:
                dc.SetBrush(wx.WHITE_BRUSH)
            x, y = bot.position
            dc.DrawCircle(x, y, 6)

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('Motion')
        self.SetClientSize((SIZE, SIZE))
        Panel(self)

def main():
    app = wx.App()
    frame = Frame()
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
