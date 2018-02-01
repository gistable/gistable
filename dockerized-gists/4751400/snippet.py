# coding=UTF-8
import time
from gevent import monkey, spawn, sleep
monkey.patch_all()
import urllib2
import Tkinter as tk

run_forever = True

class App(object):
    def __init__(self, root):
        
        self.frame = tk.Frame(root)
        self.text = tk.Text(self.frame)
        self.text.pack()
        self.entry = tk.Entry(self.frame)
        self.entry.insert(tk.END, "http://ipv4.google.com")
        self.entry.pack()

        def fetch_url():
            url = self.entry.get()
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, "Fetching...")
            data = urllib2.urlopen(url).read()
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, data)

        self.fetch_button = tk.Button(self.frame, text="Fetch URL", command=lambda : spawn(fetch_url))
        self.fetch_button.pack()

        
        def quit():
            global run_forever
            run_forever = False

        self.quit_string = tk.StringVar()
        self.quit_button = tk.Button(self.frame, textvariable=self.quit_string, command=quit)
        self.quit_button.pack()

        self.frame.pack()


        def check_for_block():
            """ Simple visual indicator if mainloop is blocked """
            i = 0
            while True:
                self.quit_string.set("Quit " + "-\|/"[i % 4])
                i += 1
                sleep(0.1)

        spawn(check_for_block)


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    while run_forever:
        root.update()
        sleep(0.01)