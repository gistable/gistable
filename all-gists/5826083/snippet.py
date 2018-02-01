import Tkinter as tk
import time

from operator import itemgetter
from math import sqrt
from random import randint
from Queue import Queue
from threading import Thread

def vdist(q, (x1,y1), (x2,y2)):
    q.put(((x1,y1), (x2,y2)))
    return sqrt((x1-x2)**2 + (y1-y2)**2)

def vclosest(q, points):
    if len(points) == 1: return float("inf")
    if len(points) == 2: return vdist(q, *points)

    xs = sorted(points, key=itemgetter(0))
    ys = sorted(points, key=itemgetter(1))

    m = len(points)/2
    left = vclosest(q, xs[:m])
    right = vclosest(q, xs[m:])
    delta = min(left, right)

    q.put(("label", delta))

    for i in xrange(len(ys)):
        for j in range(1,8):
            if i+j < len(ys):
                d = vdist(q, ys[i], ys[i+j])
                delta = min(delta, d)
                q.put(("label", delta))

    return delta

def calc(q, points):
    d = vclosest(q, points)
    q.put(("final", d))

class App(object):
    line = None

    def __init__(self, q, points, timeout=10):
        self.queue = q
        self.points = points
        self.timeout = timeout

        # create TK root object
        self.root = tk.Tk()

        # draw all UI elements
        self.draw_label()
        self.draw_canvas()
        self.draw_items()
        self.next_step()

        # run tkinter mainloop
        self.root.mainloop()

    def draw_label(self):
        self.label = tk.Label(text="")
        self.label.pack()

    def draw_canvas(self):
        self.canvas = tk.Canvas(self.root, width=600, height=600)
        self.canvas.pack()

    def draw_items(self):
        for (x, y) in self.points:
            self.canvas.create_oval(x+49,y+49,x+51,y+51,fill="blue")

    def draw_line(self, (x1,y1), (x2,y2)):
        self.remove_line()
        self.line = self.canvas.create_line(x1+50,y1+50,x2+50,y2+50,fill="red")

    def remove_line(self):
        if self.line is not None:
            self.canvas.delete(self.line)

    def next_step(self):
        (p1, p2) = self.queue.get(timeout=500)
        if p1 == "label":
            self.label.configure(text=p2)
            self.root.after(self.timeout/10, self.next_step)
        elif p1 == "final":
            self.remove_line()
            self.label.configure(text=("Minimal distance is: %s" % p2))
        else:
            self.draw_line(p1, p2)
            self.root.after(self.timeout, self.next_step)


# generate random points
q = Queue()
points = [(randint(1,500), randint(1,500)) for _ in xrange(50)]

# separate thread to calculate closest points
Thread(target=calc, args=(q, points)).run()

# run Tkinter application
App(q, points).mainloop()
