# Imports tkinter and constants
import tkinter
from tkinter.constants import *

# addition function
def add():
    a = float(num1In.get("1.0",END))
    b = float(num2In.get("1.0",END))
    ansOut['text'] = str(a + b)

#defines window
tk = tkinter.Tk()

# creates a frame (a place on which to put components)
frame = tkinter.Frame(tk, relief=RIDGE, borderwidth=2)

#packs frame to fill window
frame.pack(fill=BOTH,expand=1)

#defines a label (static text to show purporse of input)
num1Lb = tkinter.Label(frame, text = "Enter Number One: ")

#places component on a grid (colum span shows how many colums it goes through)
num1Lb.grid(row=0, column=0, columnspan=2)

#defines a text input box (a place to recieve text input)
num1In = tkinter.Text(frame, height=1, width=31)

#places component on a grid
num1In.grid(row=0, column=2, columnspan=2)

#same as with number 1
num2Lb = tkinter.Label(frame, text = "Enter Number Two: ")
num2Lb.grid(row=1, column=0, columnspan=2)
num2In = tkinter.Text(frame, height=1, width=31)
num2In.grid(row=1, column=2, columnspan=2)

#defines a button (fommand is function but without brackets)
btnAdd = tkinter.Button(frame, text="Add", command=add)

#places component on a grid
btnAdd.grid(row=3, column=0, columnspan=1)

#starts window
tk.mainloop()