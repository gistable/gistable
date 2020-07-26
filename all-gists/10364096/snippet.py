from Tkinter import *

# First create application class


class Application(Frame):

    def __init__(self, main=None):
        Frame.__init__(self, main)

        self.pack()
        self.create_widgets()

    # Create main GUI window
    def create_widgets(self):
        self.search_var = StringVar()
        self.search_var.trace("w", self.update_list)
        self.entry = Entry(self, textvariable=self.search_var, width=13)
        self.lbox = Listbox(self, width=45, height=15)

        self.entry.grid(row=0, column=0, padx=10, pady=3)
        self.lbox.grid(row=1, column=0, padx=10, pady=3)

        # Function for updating the list/doing the search.
        # It needs to be called here to populate the listbox.
        self.update_list()

    def update_list(self, *args):
        search_term = self.search_var.get()

        # Just a generic list to populate the listbox
        lbox_list = ['Adam', 'Lucy', 'Barry', 'Bob',
                     'James', 'Frank', 'Susan', 'Amanda', 'Christie']

        self.lbox.delete(0, END)

        for item in lbox_list:
                if search_term.lower() in item.lower():
                    self.lbox.insert(END, item)


root = Tk()
root.title('Filter Listbox Test')
app = Application(main=root)
print 'Starting mainloop()'
app.mainloop()
