from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import sqlite3
from openpyxl import Workbook
import os


class Ext_Func:
	def ObtainHQ(DB,QUERY):
		if(os.path.isfile(DB)==False):	#Controllo esistenza
			Ext_Func.FilExist(DB)
			return(000)
		DB = sqlite3.connect(DB)
		try:
			cursor = DB.execute(QUERY)
		except:
			print('Error: Query failed!')
			messagebox.showerror('ERROR', 'Query Failed!')
			return(000)
		print('sono passato')
		names = [description[0] for description in cursor.description]
		return(names)
	# ______________________________________________________________ fine ObrainHQ
	
	def FilExist(file):
		print('Error: File ' + file + ' not found!')
		messagebox.showerror('ERROR', 'File ' + file + ' not found!')
	# ______________________________________________________________ fine FilExist
# ______________________________________________________________ fine Ext_Func


class ExportQ_GUI:
	def __init__(self,main):
		main.title('Inseritore Query')
		main.resizable(False, False)
		main.configure(background='grey30')
		self.l1 = Label(root, text='DB file : ',background='grey30',fg='yellow', font='helvetica 10 bold')
		self.e1 = Entry(root)
		self.l3 = Label(root, text='Query : ',background='grey30',fg='yellow', font='helvetica 10 bold')
		self.t1 = Text(root)
		self.butbro = Button(main, text='browse', command=self.BrowserFile)

		# self.t1.tag_configure("keyword", foreground="#229954", font=('arial black', 10))

		self.t1.bind("<Any-KeyRelease>", self.highlight)
		self.t1.bind("<Any-ButtonRelease>", self.highlight)
		
		self.l1.grid(row=0, column=0, pady=3)
		self.e1.grid(row=0, column=1, sticky=W, ipadx = 200)
		self.butbro.grid(row=0, column=2,  ipadx = 25)
		self.l3.grid(row=1, column=0,sticky=N,pady=3)
		self.t1.grid(row=1, column=1, columnspan=2,pady=3)
		
		# aggiunta degli ultimi bottoni
		self.butread=Button(main, text='Looks at the result of the query', font='helvetica 10 bold', command=self.Reader)
		self.b1 = Button(root, text='Export Query', command=self.Save, font='helvetica 10 bold')
		self.butread.grid(row=2, column=0, sticky=W, ipadx = 40, padx=60, columnspan=2)
		self.b1.grid(row=2, column=1, ipadx = 90, sticky=E, padx=50, columnspan=2)
	# ______________________________________________________________ fine __init__	
	
		
	def highlight(self, event=None):
		# SELEZIONE COMANDI ______________________________________________________________________________________________
		# COMMAND ____________________________________________________________________________________
		self.SelezioneComandi('select ')
		self.SelezioneComandi('from')
		self.SelezioneComandi('where')
		self.SelezioneComandi('create')
		self.SelezioneComandi('attach')
		self.SelezioneComandi('detach')
		self.SelezioneComandi('drop')
		self.SelezioneComandi('insert')
		self.SelezioneComandi('pragma')
		self.SelezioneComandi('update')
		self.SelezioneComandi('delete')
		self.SelezioneComandi('having')
		self.SelezioneComandi('constraint')
		self.SelezioneComandi('joins')
		self.SelezioneComandi('union')
		self.SelezioneComandi('trigger')
		self.SelezioneComandi('index')
		self.SelezioneComandi('alter')
		self.SelezioneComandi('truncate')
		self.SelezioneComandi('views')
		
		# BOOL ________________________________________________________________________________________
		self.SelezioneBool('exist',1)
		self.SelezioneBool('or ',1)
		self.SelezioneBool('and ',1)
		self.SelezioneBool('between',1)
		self.SelezioneBool('+',0)
		self.SelezioneBool('-',0)
		self.SelezioneBool('*',0)
		self.SelezioneBool('/',0)
		self.SelezioneBool('%',0)
		self.SelezioneBool('=',0)
		self.SelezioneBool('==',0)
		self.SelezioneBool(' in ',1)
		self.SelezioneBool('!=',0)
		self.SelezioneBool('>=',0)
		self.SelezioneBool('not in',1)
		self.SelezioneBool(' is ',1)
		self.SelezioneBool('is null',1)
		self.SelezioneBool(' like',1)
		self.SelezioneBool('<>',0)
		self.SelezioneBool('<=',0)
		self.SelezioneBool('<',0)
		self.SelezioneBool('>',0)
		self.SelezioneBool('!<',0)
		self.SelezioneBool('!>',0)
		self.SelezioneBool('UNIQUE',1)
		self.SelezioneBool('glob',1)
		self.SelezioneBool('is not',1)
		self.SelezioneBool('not ',1)
		self.SelezioneBool('&',0)
		self.SelezioneBool('|',0)
		self.SelezioneBool('~',0)
		self.SelezioneBool('>>',0)
		self.SelezioneBool('<<',0)
		
		# OPTION __________________________________________________________________________
		self.SelezioneOption('order by')
		self.SelezioneOption(' table ')
		self.SelezioneOption('distinct')
		self.SelezioneOption('database')
		self.SelezioneOption(' as ')
		self.SelezioneOption(' limit')
		self.SelezioneOption('offset')
		self.SelezioneOption('group by')
		self.SelezioneOption('index by')
	# ______________________________________________________________ fine highlight
		
		
	def SelezioneComandi(self, TagTag):
		self.t1.tag_configure("keyword", foreground="#229954", font=('arial black', 10))
		# self.t1.tag_remove("keyword", "1.0", "end")
		count = IntVar()
		countfrom = IntVar()
		self.t1.mark_set("matchStart", "1.0")
		self.t1.mark_set("matchEnd", "1.0")
		while True:
			index = self.t1.search(TagTag, "matchEnd","end", count=count)
			if (index == ""): break # no match was found
			self.t1.mark_set("matchStart", index)
			self.t1.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
			self.t1.tag_add("keyword", "matchStart", "matchEnd")
		
		count = IntVar()
		countfrom = IntVar()
		self.t1.mark_set("matchStart", "1.0")
		self.t1.mark_set("matchEnd", "1.0")
		while True:
			index = self.t1.search(TagTag.upper(), "matchEnd","end", count=count)
			if (index == ""): break # no match was found
			self.t1.mark_set("matchStart", index)
			self.t1.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
			self.t1.tag_add("keyword", "matchStart", "matchEnd")
	# ______________________________________________________________ fine SelezioneComandi
	
	def SelezioneBool(self, TagTag, upper):
		self.t1.tag_configure("keywordBool", foreground="#f1c40f", font=('arial black', 10))
		# self.t1.tag_remove("keywordBool", "1.0", "end")
		count = IntVar()
		countfrom = IntVar()
		self.t1.mark_set("matchStart", "1.0")
		self.t1.mark_set("matchEnd", "1.0")
		while True:
			index = self.t1.search(TagTag, "matchEnd","end", count=count)
			if (index == ""): break # no match was found
			self.t1.mark_set("matchStart", index)
			self.t1.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
			self.t1.tag_add("keywordBool", "matchStart", "matchEnd")
		
		if (upper == 1):
			count = IntVar()
			countfrom = IntVar()
			self.t1.mark_set("matchStart", "1.0")
			self.t1.mark_set("matchEnd", "1.0")
			while True:
				index = self.t1.search(TagTag.upper(), "matchEnd","end", count=count)
				if (index == ""): break # no match was found
				self.t1.mark_set("matchStart", index)
				self.t1.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
				self.t1.tag_add("keywordBool", "matchStart", "matchEnd")
	# ______________________________________________________________ fine SelezioneBool
			
	def SelezioneOption(self, TagTag):
		self.t1.tag_configure("keywordOpt", foreground="#1A5276", font=('arial black', 10))
		# self.t1.tag_remove("keywordOpt", "1.0", "end")
		count = IntVar()
		countfrom = IntVar()
		self.t1.mark_set("matchStart", "1.0")
		self.t1.mark_set("matchEnd", "1.0")
		while True:
			index = self.t1.search(TagTag, "matchEnd","end", count=count)
			if (index == ""): break # no match was found
			self.t1.mark_set("matchStart", index)
			self.t1.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
			self.t1.tag_add("keywordOpt", "matchStart", "matchEnd")
		
		count = IntVar()
		countfrom = IntVar()
		self.t1.mark_set("matchStart", "1.0")
		self.t1.mark_set("matchEnd", "1.0")
		while True:
			index = self.t1.search(TagTag.upper(), "matchEnd","end", count=count)
			if (index == ""): break # no match was found
			self.t1.mark_set("matchStart", index)
			self.t1.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
			self.t1.tag_add("keywordOpt", "matchStart", "matchEnd")
	# ______________________________________________________________ fine SelezioneOption
			

	def Reader(self):
		if(os.path.isfile(self.e1.get())==False):	#Controllo esistenza
			Ext_Func.FilExist(self.e1.get())
			return
			
		Q_H = Ext_Func.ObtainHQ(self.e1.get(), self.t1.get('1.0', END))
		if(Q_H==000):
			return
			
		db = sqlite3.connect(self.e1.get())	# DB su cui fare la query, b = EXEL su cui inserire la query, c = query
		dbc = db.cursor()
		print('DATABASE : ' + self.e1.get())
		print('Lettura della query . . .')
		try:
			dbc.execute(self.t1.get('1.0', END))
		except:
			print('Error: Query failed!')
			messagebox.showerror('ERROR', 'Query Failed!')
			return
		QUERY = dbc.fetchall()
		db.close()

		root2=Toplevel()
		container = Frame(root2)
		container.pack(fill='both', expand=True)
	
		tree = ttk.Treeview(container, columns=Q_H, show="headings")
		vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
		tree.configure(yscrollcommand=vsb.set)
		vsb2 = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
		tree.configure(xscrollcommand=vsb2.set)
		container.grid_columnconfigure(0, weight=1)
		container.grid_rowconfigure(0, weight=1)
		tree.grid(row=0, column=0, sticky="nwse")
		vsb.grid(row=0, column=1, sticky="nwse")
		vsb2.grid(row=1, column=0, sticky="nwse")

		for col in Q_H:
			tree.heading(col, text=col.title())
		for item in QUERY:
			tree.insert('', 'end', values=item)
	# ______________________________________________________________ fine Reader
			
	def BrowserFile(self):
		fileini = askopenfilename(	initialdir=0,
									filetypes =(("Database file", "*.db3"),("Database file", "*.db"),), title = "Choose a database file.")
		self.e1.delete(0, END)
		self.e1.insert(0, fileini.replace("/", "\\"))
	# ______________________________________________________________ fine BrowserFile
	
	def Save(self):
		fileini = asksaveasfilename(	initialdir=0,
									filetypes =(("Excel","*.xlsx"),
												("Text", "*.txt")), 
									title = "Choose a file for save the query",
									defaultextension='.txt;.xlsx')					
		filename, file_extension = os.path.splitext(fileini)
		
		a = self.e1.get()	# db
		c = filename + file_extension	#nome del file completo di estensione output
		b = self.t1.get('1.0', END)	# query
		db = sqlite3.connect(a)	# a = DB su cui fare la query, b = EXEL su cui inserire la query, c = query
		dbc = db.cursor()
		
		print('DATABASE : ' + a + '\n')
		print('Export della query in corso . . .')

		try:
			dbc.execute(b)
		except:
			print('Error: Query failed!')
			messagebox.showerror('ERROR', 'Query Failed!')
			return
		QUERY_First = dbc.fetchall()
		Q_H = Ext_Func.ObtainHQ(a, b)
		QUERY = [tuple(Q_H)] + QUERY_First
		
		if (file_extension == '.xlsx'):
			MyFile = Workbook()
			ws1 = MyFile.active
			ws1.title = os.path.basename(filename)
			
			CountLine = 1
			for row in QUERY:
				CountCel = 1
				for parameter in row:
					ws1.cell(column=CountCel, row=CountLine, value="{0}".format(parameter))
					CountCel = CountCel + 1
				CountLine = CountLine + 1
			MyFile.save(c)

		elif(file_extension == '.txt'):
			# apertura del file
			filedascrivere = open(c, 'w')
			
			counter=0
			for row in QUERY:
				if not (counter==0):
					filedascrivere.write('\n')
					
				else:
					counter+=1
					
				for parameter in row:
					filedascrivere.write(str(parameter) + '\t')
			filedascrivere.close()

		print('Termine della query')
		db.commit()
		db.close()
	# ______________________________________________________________ fine Save
# termine di ExportQ_GUI ______________________________________________________________

		







root = Tk()
My_GUI = ExportQ_GUI(root)
root.mainloop()