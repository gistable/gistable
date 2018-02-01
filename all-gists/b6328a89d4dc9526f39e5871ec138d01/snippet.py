#!/usr/bin/env python

import tkinter as tk
import math
import re
from collections import ChainMap

Nrows = 5
Ncols = 5

cellre = re.compile(r'\b[A-Z][0-9]\b')


def cellname(i, j):
    return f'{chr(ord("A")+j)}{i+1}'


class Cell():
    def __init__(self, i, j, siblings, parent):
        self.row = i
        self.col = j
        self.siblings = siblings
        self.name = cellname(i, j)
        self.formula = '0'
        self.value = 0
        # Dependencies - must be updated if this cell changes
        self.deps = set()
        # Requirements - values required for this cell to calculate
        self.reqs = set()

        self.var = tk.StringVar()
        entry = self.widget = tk.Entry(parent,
                                       textvariable=self.var,
                                       justify='right')
        entry.bind('<FocusIn>', self.edit)
        entry.bind('<FocusOut>', self.update)
        entry.bind('<Return>', self.update)
        entry.bind('<Up>', self.move(-1, 0))
        entry.bind('<Down>', self.move(+1, 0))
        entry.bind('<Left>', self.move(0, -1))
        entry.bind('<Right>', self.move(0, 1))

        self.var.set(self.value)

    def move(self, rowadvance, coladvance):
        targetrow = (self.row + rowadvance) % Nrows
        targetcol = (self.col + coladvance) % Ncols

        def focus(event):
            targetwidget = self.siblings[cellname(targetrow, targetcol)].widget
            targetwidget.focus()

        return focus

    def calculate(self):
        currentreqs = set(cellre.findall(self.formula))

        # Add this cell to the new requirement's dependents
        for r in currentreqs - self.reqs:
            self.siblings[r].deps.add(self.name)
        # Add remove this cell from dependents no longer referenced
        for r in self.reqs - currentreqs:
            self.siblings[r].deps.remove(self.name)

        # Look up the values of our required cells
        reqvalues = {r: self.siblings[r].value for r in currentreqs}
        # Build an environment with these values and basic math functions
        environment = ChainMap(math.__dict__, reqvalues)
        # Note that eval is DANGEROUS and should not be used in production
        self.value = eval(self.formula, {}, environment)

        self.reqs = currentreqs
        self.var.set(self.value)

    def propagate(self):
        for d in self.deps:
            self.siblings[d].calculate()
            self.siblings[d].propagate()

    def edit(self, event):
        self.var.set(self.formula)
        self.widget.select_range(0, tk.END)

    def update(self, event):
        self.formula = self.var.get()
        self.calculate()
        self.propagate()
        # If this was after pressing Return, keep showing the formula
        if hasattr(event, 'keysym') and event.keysym == "Return":
            self.var.set(self.formula)


class SpreadSheet(tk.Frame):
    def __init__(self, rows, cols, master=None):
        super().__init__(master)
        self.rows = rows
        self.cols = cols
        self.cells = {}

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # Frame for all the cells
        self.cellframe = tk.Frame(self)
        self.cellframe.pack(side='top')

        # Column labels
        blank = tk.Label(self.cellframe)
        blank.grid(row=0, column=0)
        for j in range(self.cols):
            label = tk.Label(self.cellframe, text=chr(ord('A')+j))
            label.grid(row=0, column=j+1)

        # Fill in the rows
        for i in range(self.rows):
            rowlabel = tk.Label(self.cellframe, text=str(i + 1))
            rowlabel.grid(row=1+i, column=0)
            for j in range(self.cols):
                cell = Cell(i, j, self.cells, self.cellframe)
                self.cells[cell.name] = cell
                cell.widget.grid(row=1+i, column=1+j)


root = tk.Tk()
app = SpreadSheet(Nrows, Ncols, master=root)
app.mainloop()
