#!/usr/bin/env python

__title__ = 'Google Beatbox GUI'
__version__ = 0.1

"""
This program provides a simple GUI interface to create Google Beatbox beats.
Original idea here: http://news.ycombinator.com/item?id=1952356
Drum Sounds defined: http://news.ycombinator.com/item?id=1952531
"""

from Tkinter import *
import tkMessageBox 

class App:
    def __init__(self,parent):

        f = Frame(parent)
        f.pack(padx=15, pady=15)

        self.output_label = Label(f, text="Output")
        self.output_label.pack(side=BOTTOM, padx=10, pady=0)
        self.output = Text(f, width=36, height=4)
        self.output.pack(side=BOTTOM, padx=10, pady=0)

        self.button = Button(f, text="Bass", command=self.add_bass)
        self.button.pack(side=LEFT, padx=10, pady=10)

        self.button = Button(f, text="Snare", command=self.add_snare)
        self.button.pack(side=LEFT, padx=10, pady=10)

        self.button = Button(f, text="Hi Hat Tap", command=self.add_hi_hat_tap)
        self.button.pack(side=LEFT, padx=10, pady=10)

        self.button = Button(f, text="Better Hi Hat", command=self.add_better_hi_hat)
        self.button.pack(side=LEFT, padx=10, pady=10)

        self.button = Button(f, text="Susp. Cymbal", command=self.add_susp_cymbal)
        self.button.pack(side=LEFT, padx=10, pady=10)
        
        self.button = Button(f, text="Brush", command=self.add_brush)
        self.button.pack(side=LEFT, padx=10, pady=10)
        
        self.button = Button(f, text="Flam1", command=self.add_flam1)
        self.button.pack(side=LEFT, padx=10, pady=10)
        
        self.button = Button(f, text="Flam2", command=self.add_flam2)
        self.button.pack(side=LEFT, padx=10, pady=10)
        
        self.button = Button(f, text="Flam Tap", command=self.add_flam_tap)
        self.button.pack(side=LEFT, padx=10, pady=10)

        self.button = Button(f, text="Roll Tap", command=self.add_roll_tap)
        self.button.pack(side=LEFT, padx=10, pady=10)
        
        self.button = Button(f, text="Short Roll", command=self.add_short_roll)
        self.button.pack(side=LEFT, padx=10, pady=10)
        
        self.button = Button(f, text="Rimshot", command=self.add_rimshot)
        self.button.pack(side=LEFT, padx=10, pady=10)

        self.button = Button(f, text="[rest]", command=self.add_rest)
        self.button.pack(side=LEFT, padx=10, pady=10)

    def add_bass(self):
        self.output.insert('end', 'bk ')

    def add_snare(self):
        self.output.insert('end', 'bschk ')

    def add_hi_hat_tap(self):
        self.output.insert('end', 'krp ')
        
    def add_better_hi_hat(self):
        self.output.insert('end', 'th ')

    def add_susp_cymbal(self):
        self.output.insert('end', 'zk ')
        
    def add_brush(self):
        self.output.insert('end', 'pv ')
        
    def add_flam1(self):
        self.output.insert('end', 'tk ')
        
    def add_flam2(self):
        self.output.insert('end', 'kt ')
        
    def add_flam_tap(self):
        self.output.insert('end', 'kttp ')
        
    def add_roll_tap(self):
        self.output.insert('end', 'vk ')
        
    def add_short_roll(self):
        self.output.insert('end', 'pv ')
        
    def add_rimshot(self):
        self.output.insert('end', 'thp, ds ')

    def add_rest(self):
        self.output.insert('end', '. ')


root = Tk()
root.title(__title__)
app = App(root)
root.mainloop()