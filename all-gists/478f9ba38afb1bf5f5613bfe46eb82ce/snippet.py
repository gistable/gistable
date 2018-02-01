from random import choice
from string import ascii_lowercase, ascii_uppercase, digits
from tkinter import Tk, Entry, Button, StringVar

def random_string(length):
   return ''.join(choice(ascii_lowercase + digits + ascii_uppercase) for i in range(length))

root = Tk()
root.title('32 chars random string generator')

var = StringVar()
var.set(random_string(32))

entry = Entry(root, width=40, justify='center', textvariable=var)
entry.pack(padx=5, pady=5)

def copy_callback():
    root.clipboard_clear()
    root.clipboard_append(var.get())

def gen_callback():
    var.set(random_string(32))

button_generate = Button(root, text="Generate", command=gen_callback)
button_generate.pack(padx=5, pady=5)

button_copy = Button(root, text="Copy to clipboard", command=copy_callback)
button_copy.pack(padx=5, pady=5)

root.mainloop()